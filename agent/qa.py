# agent/qa.py
# Retrieves relevant chunks and answers questions using Google GenAI LLM.
# Includes source citations in every answer.
# Memory: retains context across multiple user turns.
#
# Retrieval strategy (hybrid):
#   1. Vector retriever with tuned MMR
#   2. BM25 retriever for exact keyword matching
#   3. Reciprocal Rank Fusion combines both

import re
import time
import json
from typing import List

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.prompts import PromptTemplate
from llama_index.core.schema import TextNode
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever

import config


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
            self.elapsed = (time.perf_counter() - self.start) * 1000
            print(f"[TIMING] {self.name}: {self.elapsed:.0f}ms")


QA_PROMPT = PromptTemplate(
    "You are a helpful personal assistant. "
    "You have access to personal memory about the user and a knowledge base. "
    "Use these sources to answer questions, but also use your own reasoning "
    "when neither source is relevant.\n\n"

    "## SOURCES\n\n"

    "MEMORY (personal information the user has shared with you):\n"
    "---------------------\n"
    "{memory_context}\n"
    "---------------------\n\n"

    "KNOWLEDGE BASE (documents you can reference):\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n\n"

    "## RULES\n\n"

    "SOURCE PRIORITY:\n"
    "  1. MEMORY — for anything personal (name, preferences, situation, past context)\n"
    "  2. KNOWLEDGE BASE — for factual questions covered in the documents\n"
    "  3. YOUR OWN REASONING — for everything else (opinions, general knowledge, "
    "explanations, topics not in the documents)\n\n"

    "MEMORY PRIORITY: If the question contains words like 'my', 'I', or 'me', "
    "check MEMORY first. Only fall back to the knowledge base if memory has "
    "nothing relevant. Cite memory answers as (Source: memory).\n\n"

    "NOT FOUND: If the question is about a specific topic covered in the knowledge "
    "base but the answer is missing, say "
    "'I couldn't find that in the knowledge base.' — nothing else.\n"
    "For everything else, use your own reasoning and do not add a citation.\n\n"

    "MULTI-PART QUESTIONS: If the user's message mixes personal context with a "
    "factual question, address both. Greet or acknowledge the personal part using "
    "memory, then answer the factual part from the knowledge base or reasoning.\n\n"

    "CITATIONS: Add (Source: filename) after facts from the knowledge base. "
    "Add (Source: memory) after facts from memory. "
    "Do NOT add citations to greetings, opinions, general reasoning, or "
    "filler sentences like 'Is there anything else I can help with?'.\n\n"

    "FORMAT:\n"
    "  - Write in plain conversational paragraphs.\n"
    "  - Use numbered lists only when the question asks for steps or a list.\n"
    "  - No markdown formatting (no **bold**, *italics*, or # headers).\n\n"

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


def build_retriever(index: VectorStoreIndex):
    """
    Builds the retrieval pipeline (hybrid: vector + BM25 + fusion):
    1. Vector retriever with tuned MMR
    2. BM25 retriever for exact keyword matching
    3. Reciprocal Rank Fusion combines both
    """
    # Vector retriever with MMR
    vector_retriever = index.as_retriever(
        vector_store_query_mode="mmr",
        similarity_top_k=config.TOP_K,
        vector_store_kwargs={"mmr_threshold": config.MMR_LAMBDA},
    )

    if config.USE_BM25:
        # Load nodes from JSON for BM25
        bm25_path = "./data/bm25_nodes.json"
        try:
            with open(bm25_path, encoding="utf-8") as f:
                nodes_data = json.load(f)
            nodes = [TextNode(**d) for d in nodes_data]
            print(f"[qa] Loaded {len(nodes)} nodes for BM25")
        except Exception as e:
            print(f"[qa] BM25 fallback: {e}")
            return vector_retriever

        bm25_retriever = BM25Retriever.from_defaults(
            nodes=nodes,
            similarity_top_k=config.BM25_TOP_K,
        )

        # Fusion: combine vector + BM25 with Reciprocal Rank Fusion
        fusion_retriever = QueryFusionRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            similarity_top_k=config.TOP_K,
            num_queries=1,
            mode="reciprocal_rerank",
            use_async=False,
        )
        return fusion_retriever

    return vector_retriever


def ask(question: str, index: VectorStoreIndex, memory=None) -> dict:
    """
    Ask a question against the index.

    Retrieval pipeline:
      1. Build retriever (vector + BM25 + fusion)
      2. Retrieve relevant nodes
      3. Build prompt (with memory context)
      4. LLM answer generation
      5. Save to memory

    Returns:
        {
            "answer": str,
            "sources": list of source labels
        }
    """
    timing_enabled = getattr(config, "DEBUG_TIMING", False)
    total_start = time.perf_counter()

    print(f"\n[qa] Question: {question[:60]}...") if timing_enabled else None

    # Get memory context if available
    memory_context = ""
    if memory:
        with Timer("0. Memory retrieval", timing_enabled):
            memory_context = memory.get_context(question)
            if memory_context:
                print(f"[qa] Retrieved {len(memory_context)} chars from memory")

    retriever = build_retriever(index)

    with Timer("1. Retrieval", timing_enabled):
        nodes = retriever.retrieve(question)
        print(f"[qa] Retrieved {len(nodes)} chunks")

    # Keyword-based relevance check: if question contains specific terms (like
    # product names, brand names, specific features), verify they appear together
    # in at least one retrieved chunk
    question_lower = question.lower()
    question_words = set(re.findall(r'\b[a-z]{4,}\b', question_lower))
    stop_words = {'what', 'does', 'have', 'from', 'with', 'that', 'this', 'when', 'where', 
                  'how', 'can', 'the', 'and', 'for', 'are', 'you', 'your', 'not', 'about', 
                  'nova', 'desk', 'desk', 'plan', 'plans', 'plan', 'using', 'about'}
    key_terms = question_words - stop_words
    
    # Check if question has a specific brand/product name or import-related terms
    specific_terms = {'zendesk', 'hipaa', 'soc', 'slack', 'api', 'import', 'export',
                      'gdpr', 'sso', 'saml', 'oauth', 'webhook', 'zapier'}
    question_specific = key_terms & specific_terms
    
    if question_specific:
        chunk_texts = [n.text.lower() for n in nodes]
        # Check if ALL specific terms appear in at least one chunk
        all_found = all(any(term in chunk for chunk in chunk_texts) for term in question_specific)
        if not all_found:
            return {
                "answer": "I couldn't find that in the provided documents.",
                "sources": []
            }

    if not nodes:
        return {
            "answer": "No relevant documents found. Try ingesting some documents first.",
            "sources": []
        }

    with Timer("2. Build prompt", timing_enabled):
        context_parts = [format_source(n) for n in nodes]
        context_str = "\n\n---\n\n".join(context_parts)
        
        # Prepend memory context if available
        if memory_context:
            full_context = f"{memory_context}\n\n---\n\n{context_str}"
        else:
            full_context = context_str
        
        prompt = QA_PROMPT.format(context_str=full_context, query_str=question)

    if getattr(config, "DEBUG_LLM", False):
        from rich.console import Console
        from rich.panel import Panel
        dbg_console = Console()
        dbg_console.print(Panel(prompt, title="[bold magenta]DEBUG: Exact Prompt Sent to LLM[/bold magenta]", border_style="magenta"))

    with Timer("3. LLM generation", timing_enabled):
        from llama_index.core import Settings
        response = Settings.llm.complete(prompt)

    if getattr(config, "DEBUG_LLM", False):
        dbg_console.print(Panel(str(response), title="[bold magenta]DEBUG: Raw LLM Response[/bold magenta]", border_style="magenta"))

    with Timer("4. Collect sources", timing_enabled):
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

    if timing_enabled:
        total_elapsed = (time.perf_counter() - total_start) * 1000
        print(f"[TIMING] Total pipeline: {total_elapsed:.0f}ms\n")

    # Save conversation to memory if available
    if memory:
        answer_text = str(response).strip()
        memory.add_message("user", question)
        memory.add_message("assistant", answer_text)

    return {
        "answer": str(response).strip(),
        "sources": list(dict.fromkeys(sources))
    }
