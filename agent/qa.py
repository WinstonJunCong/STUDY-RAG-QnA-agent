# agent/qa.py
# Retrieves relevant chunks and answers questions using the local Ollama LLM.
# Includes source citations and video timestamps in every answer.

from llama_index.core import VectorStoreIndex
from llama_index.core.prompts import PromptTemplate

import config

QA_PROMPT = PromptTemplate(
    "You are a helpful customer support assistant. "
    "Answer the question using only the information from the sources below. "
    "Keep your answer natural and conversational - like explaining to a colleague.\n\n"
    "## RULES\n"
    "- Write in plain paragraphs, no bullet points or numbered lists\n"
    "- No markdown formatting (no **bold**, *italics*, # headers, etc.)\n"
    "- If the answer is not in the sources, say \"I couldn't find that in the provided documents.\"\n"
    "- Mention the source in parentheses after relevant sentences: (Source: filename)\n\n"
    "Sources:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n\n"
    "Question: {query_str}\n\n"
    "Answer:"
)


import re


def strip_markdown(text: str) -> str:
    """Remove markdown formatting from text."""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def format_source(node) -> str:
    """Format a retrieved node with its source label, stripping markdown."""
    meta = node.metadata
    source = meta.get("source", "unknown")
    doc_type = meta.get("type", "")

    raw_text = node.text.strip()
    clean_text = strip_markdown(raw_text)

    if doc_type == "video":
        ts = meta.get("timestamp_label", "?")
        label = f"[VIDEO: {meta.get('filename', source)} @ {ts}]"
    elif doc_type == "html":
        label = f"[WEB: {meta.get('title', source)}]"
    else:
        label = f"[FILE: {meta.get('filename', source)}]"

    return f"{label}\n{clean_text}"


def ask(question: str, index: VectorStoreIndex) -> dict:
    """
    Ask a question against the index.
    Optionally uses HyDE (hypothetical document embedding) and a reranker,
    both toggled via config.USE_HYDE and config.USE_RERANKER.

    Returns:
        {
            "answer": str,
            "sources": list of source labels
        }
    """
    from llama_index.core import Settings

    # ── Step 1: Retrieve raw candidates ──────────────────────────────────────
    retriever = index.as_retriever(similarity_top_k=config.TOP_K)

    if getattr(config, "USE_HYDE", False):
        # HyDE: ask the LLM to generate a hypothetical ideal answer,
        # then embed THAT instead of the raw question for better vocab matching
        from llama_index.core.indices.query.query_transform.base import HyDEQueryTransform
        from llama_index.core.query_engine import TransformQueryEngine

        hyde = HyDEQueryTransform(include_original=True)
        base_engine = index.as_query_engine(similarity_top_k=config.TOP_K)
        hyde_engine = TransformQueryEngine(base_engine, hyde)

        # Use HyDE engine to get nodes — we have to retrieve via query then extract nodes
        hyde_response = hyde_engine.query(question)
        nodes = hyde_response.source_nodes
        print(f"[qa] HyDE retrieved {len(nodes)} chunks")
    else:
        nodes = retriever.retrieve(question)
        print(f"[qa] Standard retrieval: {len(nodes)} chunks")

    if not nodes:
        return {
            "answer": "No relevant documents found. Try ingesting some documents first.",
            "sources": []
        }

    # ── Step 2: Rerank (optional second-pass scoring) ─────────────────────────
    if getattr(config, "USE_RERANKER", False):
        try:
            from llama_index.core.postprocessor import SentenceTransformerRerank

            reranker = SentenceTransformerRerank(
                model=config.RERANKER_MODEL,
                top_n=config.TOP_N,
            )
            nodes = reranker.postprocess_nodes(nodes, query_str=question)
            print(f"[qa] Reranker kept top {len(nodes)} chunks")
        except Exception as e:
            print(f"[qa] Reranker failed, falling back to raw retrieval: {e}")

    # ── Step 3: Build prompt and call LLM ────────────────────────────────────
    context_parts = [format_source(n) for n in nodes]
    context_str = "\n\n---\n\n".join(context_parts)
    prompt = QA_PROMPT.format(context_str=context_str, query_str=question)

    if getattr(config, "DEBUG_LLM", False):
        from rich.console import Console
        from rich.panel import Panel
        dbg_console = Console()
        dbg_console.print(Panel(prompt, title="[bold magenta]🐛 DEBUG: Exact Prompt Sent to LLM[/bold magenta]", border_style="magenta"))

    response = Settings.llm.complete(prompt)

    if getattr(config, "DEBUG_LLM", False):
        dbg_console.print(Panel(str(response), title="[bold magenta]🐛 DEBUG: Raw LLM Response[/bold magenta]", border_style="magenta"))

    # ── Step 4: Collect unique source labels ─────────────────────────────────
    sources = []
    for node in nodes:
        meta = node.metadata
        doc_type = meta.get("type", "")
        if doc_type == "video":
            ts = meta.get("timestamp_label", "?")
            sources.append(f"{meta.get('filename', 'video')} at {ts}")
        elif doc_type == "html":
            sources.append(meta.get("title") or meta.get("source", "web"))
        else:
            file_path = meta.get("file_path", "")
            filename = meta.get("filename") or meta.get("source", "file")
            if file_path:
                from pathlib import Path
                proper_uri = Path(file_path).as_uri()
                sources.append(f"[link={proper_uri}]{filename}[/link] ({file_path})")
            else:
                sources.append(filename)

    return {
        "answer": str(response).strip(),
        "sources": list(dict.fromkeys(sources))  # deduplicate, preserve order
    }
