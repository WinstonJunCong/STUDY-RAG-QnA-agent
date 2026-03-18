# agent/qa.py
# Retrieves relevant chunks and answers questions using the local Ollama LLM.
# Includes source citations and video timestamps in every answer.

import re
import time

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
    
    timing_enabled = getattr(config, "DEBUG_TIMING", False)
    total_start = time.perf_counter()
    
    print(f"\n[qa] 🔍 Question: {question[:60]}...") if timing_enabled else None
    
    # ── Step 1: Setup retriever ───────────────────────────────────────────────
    with Timer("1. Setup retriever", timing_enabled):
        retriever = index.as_retriever(similarity_top_k=config.TOP_K)

    # ── Step 2: HyDE transformation (if enabled) ─────────────────────────────
    search_query = question
    if getattr(config, "USE_HYDE", False):
        with Timer("2. HyDE transformation", timing_enabled):
            from llama_index.core.indices.query.query_transform.base import HyDEQueryTransform
            from llama_index.core.schema import QueryBundle

            hyde = HyDEQueryTransform(include_original=True)
            transformed = hyde(QueryBundle(question))  # generates hypothetical doc

            if getattr(config, "DEBUG_LLM", False):
                print(f"[hyde] Hypothetical doc: {transformed.embedding_strs[0][:300]}...")

            # Use YOUR retriever with the transformed query
            search_query = transformed.embedding_strs[0]
        
        with Timer("3. Vector search", timing_enabled):
            nodes = retriever.retrieve(search_query)
        print(f"[qa] HyDE retrieved {len(nodes)} chunks")
    else:
        with Timer("3. Vector search", timing_enabled):
            nodes = retriever.retrieve(question)
        print(f"[qa] Standard retrieval: {len(nodes)} chunks")

    if not nodes:
        return {
            "answer": "No relevant documents found. Try ingesting some documents first.",
            "sources": []
        }

    # ── Step 4: Rerank (optional second-pass scoring) ─────────────────────────
    if getattr(config, "USE_RERANKER", False):
        with Timer("4. Reranking", timing_enabled):
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

    # ── Step 5: Build prompt ───────────────────────────────────────────────────
    with Timer("5. Build prompt", timing_enabled):
        context_parts = [format_source(n) for n in nodes]
        context_str = "\n\n---\n\n".join(context_parts)
        prompt = QA_PROMPT.format(context_str=context_str, query_str=question)

    if getattr(config, "DEBUG_LLM", False):
        from rich.console import Console
        from rich.panel import Panel
        dbg_console = Console()
        dbg_console.print(Panel(prompt, title="[bold magenta]🐛 DEBUG: Exact Prompt Sent to LLM[/bold magenta]", border_style="magenta"))

    # ── Step 6: LLM generation ─────────────────────────────────────────────────
    with Timer("6. LLM generation", timing_enabled):
        response = Settings.llm.complete(prompt)

    if getattr(config, "DEBUG_LLM", False):
        dbg_console.print(Panel(str(response), title="[bold magenta]🐛 DEBUG: Raw LLM Response[/bold magenta]", border_style="magenta"))

    # ── Step 7: Collect sources ────────────────────────────────────────────────
    with Timer("7. Collect sources", timing_enabled):
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

    # ── Summary ────────────────────────────────────────────────────────────────
    if timing_enabled:
        total_elapsed = (time.perf_counter() - total_start) * 1000
        print(f"[TIMING] Total pipeline: {total_elapsed:.0f}ms\n")
    
    return {
        "answer": str(response).strip(),
        "sources": list(dict.fromkeys(sources))  # deduplicate, preserve order
    }
