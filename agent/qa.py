# agent/qa.py
# Retrieves relevant chunks and answers questions using the local Ollama LLM.
# Includes source citations and video timestamps in every answer.

from llama_index.core import VectorStoreIndex
from llama_index.core.prompts import PromptTemplate

import config

QA_PROMPT = PromptTemplate(
    "You are a strict document-based assistant. "
    "You ONLY answer using information explicitly stated in the source excerpts provided below. "
    "You do NOT infer, assume, or use any external knowledge.\n\n"

    "## ANSWER RULES\n"
    "- If the answer is fully covered in the sources: answer completely and accurately.\n"
    "- If the answer spans multiple sources: combine ALL relevant information from ALL sources into one complete answer.\n"
    "- If sources contain conflicting information: present BOTH versions, state which source says what, and flag the conflict.\n"
    "- If the question has multiple parts: answer EVERY part separately.\n"
    "- If information exists across multiple plans, tiers, or options: list ALL of them — never summarize into just one.\n"
    "- If the answer is not found in ANY source: respond only with 'I couldn't find that in the provided documents.'\n"
    "- Do NOT add disclaimers, opinions, suggestions, or information not present in the sources.\n\n"

    "## CITATION RULES\n"
    "- Every sentence or claim MUST be followed immediately by its source citation.\n"
    "- Use the EXACT source label as it appears in the sources below — do not modify, shorten, or rephrase it.\n"
    "- If a claim is supported by multiple sources, list all of them: [FILE: a.md][FILE: b.md]\n"
    "- Do not group all citations at the end — cite inline after each individual claim.\n"
    "- Never invent, guess, or paraphrase a source label.\n\n"
    "Never generate URLs, anchor links, or file paths that are not explicitly present in the sources.\n"
    
    "## CITATION FORMAT (use exactly as shown)\n"
    "  [FILE: filename]         → for document files\n"
    "  [VIDEO: filename @ time] → for video sources\n"
    "  [WEB: title]             → for web sources\n\n"

    "Sources:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n\n"

    "Question: {query_str}\n\n"

    "Answer:"
)


def format_source(node) -> str:
    """Format a retrieved node with its source label."""
    meta = node.metadata
    source = meta.get("source", "unknown")
    doc_type = meta.get("type", "")

    if doc_type == "video":
        ts = meta.get("timestamp_label", "?")
        label = f"[VIDEO: {meta.get('filename', source)} @ {ts}]"
    elif doc_type == "html":
        label = f"[WEB: {meta.get('title', source)}]"
    else:
        label = f"[FILE: {meta.get('filename', source)}]"
        # label = f"[FILE: {meta.get('file_path', source)}]"

    return f"{label}\n{node.text.strip()}"


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
            from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker
            from llama_index.core.schema import QueryBundle

            reranker = FlagEmbeddingReranker(
                model=config.RERANKER_MODEL,
                top_n=config.TOP_N,
            )
            nodes = reranker.postprocess_nodes(nodes, query_bundle=QueryBundle(query_str=question))
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
            sources.append(f"{meta.get('filename', 'video')} @ {ts}")
        elif doc_type == "html":
            sources.append(meta.get("title") or meta.get("source", "web"))
        else:
            file_path = meta.get("file_path", "")
            filename = meta.get("filename") or meta.get("source", "file")
            if file_path:
                from pathlib import Path
                proper_uri = Path(file_path).as_uri()
                sources.append(f"[link={proper_uri}]{filename}[/link] [dim]({file_path})[/dim]")
            else:
                sources.append(filename)

    return {
        "answer": str(response).strip(),
        "sources": list(dict.fromkeys(sources))  # deduplicate, preserve order
    }
