# agent/qa.py
# Retrieves relevant chunks and answers questions using the local Ollama LLM.
# Includes source citations and video timestamps in every answer.

from llama_index.core import VectorStoreIndex
from llama_index.core.prompts import PromptTemplate

import config

QA_PROMPT = PromptTemplate(
    "You are a helpful assistant. Answer the question using ONLY the source excerpts below.\n"
    "Always mention which source(s) your answer comes from.\n"
    "If the answer is not in the sources, say: 'I couldn't find that in the provided documents.'\n\n"
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

    return f"{label}\n{node.text.strip()}"


def ask(question: str, index: VectorStoreIndex) -> dict:
    """
    Ask a question against the index.

    Returns:
        {
            "answer": str,
            "sources": list of source labels
        }
    """
    retriever = index.as_retriever(similarity_top_k=config.TOP_K)
    nodes = retriever.retrieve(question)
    # print(f"[qa] Retrieved {len(nodes)} relevant chunks for the question: '{question}'")
    if not nodes:
        return {
            "answer": "No relevant documents found. Try ingesting some documents first.",
            "sources": []
        }
    # print(f"[qa] Sources of retrieved chunks:")
    # for node in nodes:
        # print(f"   - {format_source(node)}")
    # Build context string with source labels
    context_parts = [format_source(n) for n in nodes]
    context_str = "\n\n---\n\n".join(context_parts)
    # print(f"[qa] Built context string for LLM (truncated to 1000 chars):\n{context_str[:1000]}...\n")
    # Build prompt manually and call LLM
    from llama_index.core import Settings
    print(f"[debug] LLM at query time = {Settings.llm.model}") 
    prompt = QA_PROMPT.format(context_str=context_str, query_str=question)
    # print(f"[qa] Final prompt to LLM (truncated to 1000 chars):\n{prompt[:1000]}...\n")
    response = Settings.llm.complete(prompt)
    # print(f"[qa] Raw response from LLM:\n{response}\n")
    # Collect unique source labels
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
            sources.append(meta.get("filename") or meta.get("source", "file"))

    return {
        "answer": str(response).strip(),
        "sources": list(dict.fromkeys(sources))  # deduplicate, preserve order
    }
