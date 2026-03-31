# agent/qa.py
# Retrieves relevant chunks and answers questions using the local Ollama LLM.
# Includes source citations in every answer.
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
    "You are a helpful customer support assistant. "
    "Answer the question using only the information from the sources below. "
    "Keep your answer natural and conversational.\n\n"

    "## ANSWER RULES\n\n"
    "RELEVANCE FILTER: Before combining sources, identify exactly what the "
    "question asks for. Only use chunks that directly answer that specific "
    "question. Discard chunks that answer different questions.\n\n"
    "COMPLETENESS: If answering requires information from multiple sources, "
    "combine them into one complete answer without repetition.\n\n"

    "SCOPE: Answer exactly what was asked. Do not add unrequested information.\n"
    "  - 'What is NovaDesk?' → describe the core product only, not pricing or integrations.\n"
    "  - 'How do I set up NovaDesk?' → include ALL setup steps, do not truncate.\n"
    "  - 'What discount do non-profits get?' → include ALL groups mentioned "
    "(e.g. non-profits AND educational institutions), not just one.\n\n"

    "PRICING QUESTIONS: For questions about plan costs, extract ALL pricing details "
    "from the sources:\n"
    "  - Monthly price per agent\n"
    "  - Agent seat limits\n"
    "  - Annual/discount pricing (e.g. 20% off annually)\n"
    "  - Trial information\n"
    "  Example correct: '$49 per agent per month, up to 15 agents, 20% off annually'\n"
    "  Example WRONG:   '$49 per agent per month' (missing agent limit and discount)\n\n"

    "FORMAT:\n"
    "  - Write in plain paragraphs. Only use numbered lists when the question "
    "explicitly asks to 'list', 'summarize all', or requests step-by-step instructions.\n"
    "  - No markdown formatting (no **bold**, *italics*, or # headers).\n\n"

    "NOT FOUND: If the answer is not in the sources, say "
    "'I couldn't find that in the provided documents.' — one sentence, nothing else. "
    "Do NOT suggest alternatives, workarounds, or related features.\n\n"
    
    "RELEVANCE GATE: If the retrieved sources do NOT contain information that "
    "directly answers the question, respond with ONLY "
    "'I couldn't find that in the provided documents.' — nothing else. "
    "Do NOT add general information about NovaDesk, unrelated features, or "
    "other topics mentioned in the sources.\n\n"

    "YES/NO QUESTIONS: If the direct answer is No, your FIRST word must be 'No.'\n"
    "  - Correct:   'No, the AI Bot is only available on Growth and Enterprise plans.'\n"
    "  - Incorrect: 'The AI Bot is not available on the Starter plan, but...'\n"
    "  - Incorrect: 'Yes, but only on Growth and Enterprise.'\n"
    "  - SDK/feature exists but no standalone product: Lead with what does NOT exist, "
    "then mention what does. Example: 'NovaDesk does not have a standalone mobile app. "
    "However, native SDKs for iOS and Android are available for integrating live chat "
    "into mobile apps.'\n\n"

    "CONFLICT DETECTION: Only flag a conflict if the SAME specific fact has "
    "different values in different sources.\n"
    "  - REAL conflict:   Source A says first response = 30 min, "
    "Source B says 1 hour for the same ticket priority → Flag it.\n"
    "  - FALSE conflict:  Source A says Starter has 3 agents, "
    "Source B says Growth has 15 → Different plans, not a conflict.\n\n"

    "CONFLICT CITATION (CRITICAL): If multiple sources provide DIFFERENT values "
    "for the SAME metric, you MUST include the ACTUAL VALUE from EACH source.\n"
    "  - WRONG: 'According to [doc 12], the urgent SLA is 30 min. However, "
    "[doc 11] shows the current default is 1 hour.'\n"
    "  - CORRECT: 'According to [doc 11], the urgent SLA first response is 1 hour. "
    "According to [doc 12], the urgent SLA first response is 30 minutes (legacy).'\n"
    "  - Do NOT say 'verify settings' without stating the actual conflicting values.\n\n"

    "CITATIONS: After each sentence or claim, add the source in parentheses: "
    "(Source: filename)\n"
    "  - If two sources say the same thing, cite both: "
    "(Source: file_a.md, file_b.md)\n"
    "  - If two sources genuinely conflict, present both values and state "
    "which source says what.\n\n"

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


def ask(question: str, index: VectorStoreIndex) -> dict:
    """
    Ask a question against the index.

    Retrieval pipeline:
      1. Build retriever (vector + BM25 + fusion)
      2. Retrieve relevant nodes
      3. Build prompt
      4. LLM answer generation

    Returns:
        {
            "answer": str,
            "sources": list of source labels
        }
    """
    timing_enabled = getattr(config, "DEBUG_TIMING", False)
    total_start = time.perf_counter()

    print(f"\n[qa] Question: {question[:60]}...") if timing_enabled else None

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
        prompt = QA_PROMPT.format(context_str=context_str, query_str=question)

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

    return {
        "answer": str(response).strip(),
        "sources": list(dict.fromkeys(sources))
    }
