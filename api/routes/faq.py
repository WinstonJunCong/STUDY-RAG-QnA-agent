# api/routes/faq.py
# FAQ management endpoints

import os
from fastapi import APIRouter, HTTPException
from api.models import (
    FAQListResponse,
    FAQEntry,
    FAQGenerateRequest,
    FAQGenerateResponse,
    FAQApproveResponse
)
import config
from services.query_logger import get_query_logger

router = APIRouter()


def _parse_faq_file(filepath: str) -> list:
    """Parse FAQ entries from markdown file."""
    if not os.path.exists(filepath):
        return []

    entries = []
    current_question = None
    current_answer = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("## "):
                if current_question:
                    entries.append(FAQEntry(
                        question=current_question,
                        answer="\n".join(current_answer).strip()
                    ))
                current_question = line[3:].strip()
                current_answer = []
            elif current_question and line:
                current_answer.append(line)

        if current_question:
            entries.append(FAQEntry(
                question=current_question,
                answer="\n".join(current_answer).strip()
            ))

    return entries


@router.get("", response_model=FAQListResponse)
async def list_faqs():
    """List approved FAQ entries."""
    entries = _parse_faq_file(config.FAQ_ENTRIES_FILE)
    return FAQListResponse(
        entries=entries,
        count=len(entries)
    )


@router.get("/drafts", response_model=FAQListResponse)
async def list_drafts():
    """List FAQ draft entries."""
    entries = _parse_faq_file(config.FAQ_DRAFTS_FILE)
    return FAQListResponse(
        entries=entries,
        count=len(entries)
    )


@router.post("/generate", response_model=FAQGenerateResponse)
async def generate_faqs(request: FAQGenerateRequest):
    """
    Generate FAQ drafts from recent queries.
    Groups similar queries (semantic similarity) and generates draft FAQs.
    """
    logger = get_query_logger()
    hours = 336 if config.FAQ_SCHEDULE == "biweekly" else 168

    queries = logger.get_recent_queries(hours=hours)

    if not queries:
        return FAQGenerateResponse(
            status="no_queries",
            drafts_count=0,
            message="No queries logged yet"
        )

    # Group queries by similarity (simple word overlap for now)
    from collections import defaultdict
    groups = defaultdict(list)

    for q in queries:
        text = q["query_text"].lower()
        words = set(text.split())
        key = tuple(sorted(words))
        groups[key].append(q)

    # Filter groups with enough queries
    min_count = request.min_count or config.MIN_QUERY_COUNT
    threshold = request.similarity_threshold or config.SIMILARITY_THRESHOLD

    drafts = []
    for key, qs in groups.items():
        if len(qs) >= min_count:
            # Use the most common query as representative
            representative = max(qs, key=lambda x: len(x["query_text"]))
            drafts.append({
                "question": representative["query_text"],
                "count": len(qs)
            })

    # Write to drafts file
    if drafts:
        with open(config.FAQ_DRAFTS_FILE, "w", encoding="utf-8") as f:
            f.write("# FAQ Drafts (Pending Human Review)\n\n")
            f.write("Generated from query log. Edit as needed and move to faq_entries.md.\n\n")
            for i, draft in enumerate(drafts, 1):
                f.write(f"## {i}. {draft['question']}\n\n")
                f.write(f"_Seen {draft['count']} times_\n\n")
                f.write("[Add answer here]\n\n")

    return FAQGenerateResponse(
        status="ok",
        drafts_count=len(drafts),
        message=f"Generated {len(drafts)} FAQ drafts"
    )


@router.post("/approve", response_model=FAQApproveResponse)
async def approve_faqs():
    """
    Approve FAQ drafts and trigger re-ingest.
    Merges approved drafts into faq_entries.md and rebuilds index.
    """
    drafts_path = config.FAQ_DRAFTS_FILE
    entries_path = config.FAQ_ENTRIES_FILE

    if not os.path.exists(drafts_path):
        raise HTTPException(status_code=404, detail="No drafts found")

    # Read drafts
    with open(drafts_path, "r", encoding="utf-8") as f:
        drafts_content = f.read()

    # Append to entries (simple approach - human should edit first)
    entries_content = ""
    if os.path.exists(entries_path):
        with open(entries_path, "r", encoding="utf-8") as f:
            entries_content = f.read()

    with open(entries_path, "w", encoding="utf-8") as f:
        if entries_content:
            f.write(entries_content + "\n\n")
        f.write("# Approved FAQs\n\n")
        f.write(drafts_content)

    # Rebuild index
    from services.rag_service import get_rag_service
    rag = get_rag_service()
    try:
        rag.ingest(force_rebuild=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Index rebuild failed: {str(e)}")

    return FAQApproveResponse(
        status="ok",
        entries_count=len(_parse_faq_file(entries_path)),
        message="FAQ approved and index rebuilt"
    )
