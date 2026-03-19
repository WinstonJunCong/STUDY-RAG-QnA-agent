# agent/qa.py
# Retrieves relevant chunks and answers questions using the local Ollama LLM.
# Includes source citations in every answer.
#
# Retrieval strategy (configurable in config.py):
#   USE_MULTI_QUERY  — generate N rule-based rephrasings, run parallel vector searches,
#                      merge + deduplicate the candidate pool (no LLM needed, ~0 ms).
#   USE_MMR          — Maximal Marginal Relevance post-filter: selects TOP_N chunks that
#                      are both relevant AND diverse (pure vector math, no model load).
#
# Both supersede the previous HyDE + cross-encoder reranker approach, which was:
#   - Too slow (HyDE adds a synchronous LLM call; reranker adds 1-3 s CPU inference)
#   - Poorly suited to niche/technical corpora (LLM hallucinates unfamiliar vocabulary;
#     bge-reranker-base wasn't fine-tuned on your domain)

import re
import time
import math
from typing import List

class Timer:
    """Context manager for timing code blocks"""
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.start = None
        self.elapsed = None

    def __enter__(self):
        if self.enabled:
            self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        if self.enabled:
            self.elapsed = (time.perf_counter() - self.start) * 1000  # ms
            print(f"[TIMING] {self.name}: {self.elapsed:.0f}ms")


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
    "- If the answer is not in the sources, say \"I couldn't find that in the provided documents.\" ONLY. Do NOT suggest alternatives, workarounds, or other products.\n"
    "- If the answer is \"No\", state it clearly and prominently in the first sentence before adding any additional context.\n"
    "- Mention the source in parentheses after relevant sentences: (Source: filename)\n"
    "- If multiple sources provide DIFFERENT information, present BOTH versions and explicitly note they conflict\n"
    "- Extract ALL relevant details from ALL sources, even if spread across multiple documents\n"
    "- Never add clarifications, caveats, or inferences not explicitly stated in sources\n\n"
    "Sources:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n\n"
    "Question: {query_str}\n\n"
    "Answer:"
)


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


# ── Multi-Query: rule-based query expansion ────────────────────────────────────

def expand_query(question: str, n: int) -> List[str]:
    """
    Generate up to `n` rephrasings of `question` using local string patterns.
    No LLM involved — deterministic, instant, preserves exact domain vocabulary.

    Strategy (you can extend this list for your specific domain):
      1. Original question (always included)
      2. Shorter noun-phrase form (strip leading question words)
      3. "How to / What is / Where is …" reformulation
      4. Keyword extraction variant (nouns only, stripped of filler)
    """
    variants = [question]

    q = question.strip().rstrip("?").strip()

    # Variant 2 — strip common question starters to get a noun phrase
    stripped = re.sub(
        r"^(what is|what are|how (do|does|to|can)|where (is|are)|when (is|does)|"
        r"can (i|you|we)|is (there|it|this)|tell me (about|how)|explain)\s+",
        "", q, flags=re.IGNORECASE
    ).strip()
    if stripped and stripped.lower() != q.lower():
        variants.append(stripped)

    # Variant 3 — reformulate as "how to …" or "definition of …"
    lower = q.lower()
    if lower.startswith("what is") or lower.startswith("what are"):
        noun = re.sub(r"^what (is|are)\s+", "", q, flags=re.IGNORECASE).strip()
        variants.append(f"definition of {noun}")
    elif lower.startswith("how"):
        noun = re.sub(r"^how (do|does|to|can)\s+(i|you|we|one)?\s*", "", q, flags=re.IGNORECASE).strip()
        if noun:
            variants.append(f"steps to {noun}")
    else:
        # Generic "how to …" prefix
        variants.append(f"how to {q.lower()}")

    # Variant 4 — keyword bag (remove stopwords, join remaining tokens)
    stopwords = {
        "a","an","the","is","are","was","were","be","been","being",
        "have","has","had","do","does","did","will","would","shall","should",
        "may","might","can","could","must","ought","to","of","in","on","at",
        "by","for","with","about","against","between","through","during",
        "before","after","above","below","from","up","down","out","off",
        "over","under","again","further","then","once","i","you","we","it",
        "this","that","these","those","what","where","when","who","how","why",
        "tell","me","explain","please"
    }
    keywords = [w for w in re.split(r"\W+", q) if w.lower() not in stopwords and len(w) > 2]
    if len(keywords) >= 2:
        variants.append(" ".join(keywords))

    # Deduplicate (preserve order) and trim to n
    seen = set()
    result = []
    for v in variants:
        key = v.lower().strip()
        if key not in seen and v.strip():
            seen.add(key)
            result.append(v.strip())
        if len(result) >= n:
            break

    return result


# ── MMR: Maximal Marginal Relevance ───────────────────────────────────────────

def _cosine_sim(a: List[float], b: List[float]) -> float:
    """Cosine similarity between two embedding vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def mmr_select(nodes, query_embedding: List[float], top_n: int, lam: float):
    """
    Maximal Marginal Relevance selection.

    For each step, picks the candidate that maximises:
        lam * relevance(node, query) - (1 - lam) * max_similarity(node, selected)

    Args:
        nodes:           list of NodeWithScore (must have .node.embedding set)
        query_embedding: embedding of the original user question
        top_n:           number of chunks to keep
        lam:             trade-off (0 = pure diversity, 1 = pure relevance)

    Returns:
        Ordered list of up to top_n nodes.
    """
    if not nodes:
        return []

    # Filter out nodes that have no embedding stored (shouldn't happen with ChromaDB,
    # but be defensive so we never crash)
    embeddable = [n for n in nodes if getattr(n.node, "embedding", None)]
    not_embeddable = [n for n in nodes if not getattr(n.node, "embedding", None)]

    if not embeddable:
        # Fall back: return by original score order
        return sorted(nodes, key=lambda n: n.score or 0, reverse=True)[:top_n]

    selected = []
    remaining = list(embeddable)

    while remaining and len(selected) < top_n:
        best_node = None
        best_score = float("-inf")

        for candidate in remaining:
            rel = _cosine_sim(candidate.node.embedding, query_embedding)
            if selected:
                redundancy = max(
                    _cosine_sim(candidate.node.embedding, s.node.embedding)
                    for s in selected
                )
            else:
                redundancy = 0.0

            mmr_score = lam * rel - (1 - lam) * redundancy
            if mmr_score > best_score:
                best_score = mmr_score
                best_node = candidate

        selected.append(best_node)
        remaining.remove(best_node)

    # Append any nodes that had no embedding, up to top_n limit
    for n in not_embeddable:
        if len(selected) >= top_n:
            break
        selected.append(n)

    return selected


# ── Main entry point ──────────────────────────────────────────────────────────

def ask(question: str, index: VectorStoreIndex) -> dict:
    """
    Ask a question against the index.

    Retrieval pipeline (all steps togglable via config.py):
      1. Multi-Query expansion  (USE_MULTI_QUERY)  — rule-based, no LLM
      2. Parallel vector search per variant
      3. Merge + deduplicate candidates by node ID
      4. MMR post-filter        (USE_MMR)           — relevance × diversity
      5. LLM answer generation

    Returns:
        {
            "answer": str,
            "sources": list of source labels
        }
    """
    from llama_index.core import Settings

    timing_enabled = getattr(config, "DEBUG_TIMING", False)
    total_start = time.perf_counter()

    print(f"\n[qa] 🔍 Question: {question[:60]}...") if timing_enabled else None

    top_k = config.TOP_K
    top_n = getattr(config, "TOP_N", 5)
    use_multi_query = getattr(config, "USE_MULTI_QUERY", True)
    use_mmr = getattr(config, "USE_MMR", True)
    lam = getattr(config, "MMR_LAMBDA", 0.6)
    multi_query_count = getattr(config, "MULTI_QUERY_COUNT", 3)

    retriever = index.as_retriever(similarity_top_k=top_k)

    # ── Step 1: Query expansion ───────────────────────────────────────────────
    with Timer("1. Query expansion", timing_enabled):
        if use_multi_query:
            queries = expand_query(question, multi_query_count)
            print(f"[qa] Multi-query variants ({len(queries)}): {queries}")
        else:
            queries = [question]

    # ── Step 2: Parallel vector searches ─────────────────────────────────────
    with Timer("2. Vector search(es)", timing_enabled):
        all_nodes = []
        seen_ids = set()

        for q in queries:
            hits = retriever.retrieve(q)
            for n in hits:
                nid = n.node.node_id
                if nid not in seen_ids:
                    seen_ids.add(nid)
                    all_nodes.append(n)

        print(f"[qa] Merged pool: {len(all_nodes)} unique chunks from {len(queries)} queries")

    if not all_nodes:
        return {
            "answer": "No relevant documents found. Try ingesting some documents first.",
            "sources": []
        }

    # ── Step 3: MMR selection ─────────────────────────────────────────────────
    if use_mmr:
        with Timer("3. MMR selection", timing_enabled):
            try:
                query_embedding = Settings.embed_model.get_text_embedding(question)
                nodes = mmr_select(all_nodes, query_embedding, top_n=top_n, lam=lam)
                print(f"[qa] MMR kept top {len(nodes)} chunks (λ={lam})")
            except Exception as e:
                print(f"[qa] MMR failed, falling back to score-ordered top-{top_n}: {e}")
                nodes = sorted(all_nodes, key=lambda n: n.score or 0, reverse=True)[:top_n]
    else:
        # No MMR — just take the highest-scored chunks
        nodes = sorted(all_nodes, key=lambda n: n.score or 0, reverse=True)[:top_n]
        print(f"[qa] Score-ordered top {len(nodes)} chunks (MMR disabled)")

    # ── Step 4: Build prompt ──────────────────────────────────────────────────
    with Timer("4. Build prompt", timing_enabled):
        context_parts = [format_source(n) for n in nodes]
        context_str = "\n\n---\n\n".join(context_parts)
        prompt = QA_PROMPT.format(context_str=context_str, query_str=question)

    if getattr(config, "DEBUG_LLM", False):
        from rich.console import Console
        from rich.panel import Panel
        dbg_console = Console()
        dbg_console.print(Panel(prompt, title="[bold magenta]🐛 DEBUG: Exact Prompt Sent to LLM[/bold magenta]", border_style="magenta"))

    # ── Step 5: LLM generation ────────────────────────────────────────────────
    with Timer("5. LLM generation", timing_enabled):
        response = Settings.llm.complete(prompt)

    if getattr(config, "DEBUG_LLM", False):
        dbg_console.print(Panel(str(response), title="[bold magenta]🐛 DEBUG: Raw LLM Response[/bold magenta]", border_style="magenta"))

    # ── Step 6: Collect sources ───────────────────────────────────────────────
    with Timer("6. Collect sources", timing_enabled):
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

    # ── Summary ───────────────────────────────────────────────────────────────
    if timing_enabled:
        total_elapsed = (time.perf_counter() - total_start) * 1000
        print(f"[TIMING] Total pipeline: {total_elapsed:.0f}ms\n")

    return {
        "answer": str(response).strip(),
        "sources": list(dict.fromkeys(sources))  # deduplicate, preserve order
    }
