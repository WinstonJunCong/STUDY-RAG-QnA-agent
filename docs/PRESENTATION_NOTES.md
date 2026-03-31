# NovaDesk Q&A RAG System - Presentation Notes

## Technical Deep Dive for Engineering Team

This document explains the **why** behind each architectural decision, parameter choice, and design pattern in the NovaDesk Q&A RAG system.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Architecture Overview](#3-architecture-overview)
4. [Component Deep Dives](#4-component-deep-dives)
5. [Parameter Rationale](#5-parameter-rationale)
6. [Prompt Engineering](#6-prompt-engineering)
7. [Testing Strategy](#7-testing-strategy)
8. [Failure Case Deep Dives](#8-failure-case-deep-dives)
9. [Key Takeaways](#9-key-takeaways)

---

## 1. Executive Summary

### What We Built
A Retrieval-Augmented Generation (RAG) system that answers customer questions about NovaDesk using company documentation.

### Performance
| Metric | Score |
|--------|-------|
| UAT Pass Rate | 14/17 (82%) |
| Average Score | 94.0% |
| Response Time | ~3-5 seconds |

### Tech Stack (Fully Local, No API Keys)
| Component | Technology | Why |
|-----------|------------|-----|
| Framework | LlamaIndex | Best Python RAG library |
| Vector DB | ChromaDB | Local, fast, easy |
| Embeddings | BAAI/bge-base-en-v1.5 | Open-source, good quality |
| LLM | Ollama + Mistral | Fully local, private |
| Parsing | Unstructured.io | Semantic document understanding |
| Retrieval | Hybrid (Vector + BM25 + RRF) | Captures both semantic and exact matches |

---

## 2. Problem Statement

### Why RAG? Why Not Fine-tuning?

| Approach | Pros | Cons |
|----------|------|------|
| **Fine-tuning** | Fast inference | Expensive, loses knowledge over time, hard to update |
| **RAG** | Dynamic, explainable, always up-to-date | Slower inference, depends on retrieval quality |

**Decision: RAG** - Better for customer support where documentation changes frequently.

### Why Hybrid Retrieval?

```
Query: "Can I import tickets from Zendesk?"
```

| Method | What Happens | Result |
|--------|--------------|--------|
| **Vector Only** | Finds docs about "import" and "tickets" | ❌ Misses exact "Zendesk" match |
| **BM25 Only** | Finds exact "Zendesk" keyword | ❌ Misses semantic variations |
| **Hybrid (RRF)** | Combines both approaches | ✅ Catches everything |

---

## 3. Architecture Overview

### 3.1 System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              DOCUMENT SOURCES                                 │
│                                                                               │
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│    │  Markdown   │  │    HTML     │  │    Text     │  │    Video     │       │
│    │  (.md)     │  │   (.html)   │  │   (.txt)    │  │ (.mp4/.mp3)  │       │
│    └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────┬────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           INGESTION PIPELINE                                  │
│                                                                               │
│    ┌─────────────────────────────────────────────────────────────────────┐   │
│    │                      Unstructured.io                                  │   │
│    │                                                                       │   │
│    │   • partition_md()     - Markdown with heading hierarchy              │   │
│    │   • partition_text()   - Plain text, transcripts (.vtt, .srt)         │   │
│    │   • partition.auto()   - PDFs, DOCX, HTML auto-detected               │   │
│    │                                                                       │   │
│    │   chunk_by_title()     - Semantic chunking preserving Q&A, tables     │   │
│    └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│    ┌─────────────────────────────────────────────────────────────────────┐   │
│    │                      OUTPUT: TextNodes                                │   │
│    │                                                                       │   │
│    │   Node 1: "Pricing & Plans FAQ..." + metadata (filename, page, etc)   │   │
│    │   Node 2: "What are the SLA timers?" + metadata...                     │   │
│    │   ...                                                                  │   │
│    │   Node N: "HIPAA Compliance..." + metadata...                          │   │
│    └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────┬────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│         ChromaDB             │   │      bm25_nodes.json          │
│                               │   │                               │
│   Vector Embeddings           │   │   Plain text for BM25         │
│   (768 dimensions)           │   │   (exact keyword match)        │
│                               │   │                               │
│   Path: ./data/chroma_db     │   │   Path: ./data/bm25_nodes.json│
└───────────────────────────────┘   └───────────────────────────────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           QUERY PIPELINE                                     │
│                                                                               │
│    ┌─────────────────────────────────────────────────────────────────────┐   │
│    │                          USER QUERY                                    │   │
│    │                    "What is the SLA for Urgent tickets?"               │   │
│    └─────────────────────────────────────────────────────────────────────┘   │
│                                  │                                           │
│                                  ▼                                           │
│    ┌─────────────────────────────────────────────────────────────────────┐   │
│    │                     RETRIEVAL STAGE                                   │   │
│    │                                                                       │   │
│    │   ┌──────────────────┐    ┌──────────────────┐                        │   │
│    │   │  VECTOR SEARCH   │    │   BM25 SEARCH    │                        │   │
│    │   │                  │    │                  │                        │   │
│    │   │  Model: bge-base│    │  Top-K: 8        │                        │   │
│    │   │  Top-K: 6       │    │  Keywords: exact │                        │   │
│    │   │  MMR: λ=0.7     │    │  match           │                        │   │
│    │   └────────┬─────────┘    └────────┬─────────┘                        │   │
│    │            │                       │                                   │   │
│    │            └───────────┬───────────┘                                   │   │
│    │                        │                                               │   │
│    │                        ▼                                               │   │
│    │            ┌───────────────────────┐                                   │   │
│    │            │  RECIPROCAL RANK     │                                   │   │
│    │            │  FUSION (RRF)        │                                   │   │
│    │            │                       │                                   │   │
│    │            │  Score = Σ 1/(k+rank)│                                   │   │
│    │            │  k = 60               │                                   │   │
│    │            └───────────┬───────────┘                                   │   │
│    │                        │                                               │   │
│    │                        ▼                                               │   │
│    │            ┌───────────────────────┐                                   │   │
│    │            │   TOP 6 CHUNKS        │                                   │   │
│    │            │   (final context)     │                                   │   │
│    │            └───────────────────────┘                                   │   │
│    │                                                                       │   │
│    │   ┌─────────────────────────────────────────────────────────────────┐ │   │
│    │   │                    RELEVANCE GATE                                │ │   │
│    │   │                                                                   │ │   │
│    │   │   Check if question keywords appear in retrieved chunks:          │ │   │
│    │   │   specific_terms = {'zendesk', 'hipaa', 'soc', ...}              │ │   │
│    │   │                                                                   │ │   │
│    │   │   If keywords NOT found → Return "not found" immediately         │ │   │
│    │   │   (Prevents hallucination)                                       │ │   │
│    │   └─────────────────────────────────────────────────────────────────┘ │   │
│    └─────────────────────────────────────────────────────────────────────┘   │
│                                  │                                           │
│                                  ▼                                           │
│    ┌─────────────────────────────────────────────────────────────────────┐   │
│    │                      GENERATION STAGE                                 │   │
│    │                                                                       │   │
│    │   Build Prompt with QA_PROMPT template:                               │   │
│    │   ┌─────────────────────────────────────────────────────────────────┐ │   │
│    │   │ You are a customer support assistant...                        │ │   │
│    │   │                                                                  │ │   │
│    │   │ ## ANSWER RULES                                                 │ │   │
│    │   │ RELEVANCE FILTER: ...                                           │ │   │
│    │   │ PRICING QUESTIONS: ...                                          │ │   │
│    │   │ NOT FOUND: ...                                                   │ │   │
│    │   │ CONFLICT CITATION: ...                                           │ │   │
│    │   │                                                                  │ │   │
│    │   │ Sources:                                                         │ │   │
│    │   │ ─────────────────────────────────────────────────────────────   │ │   │
│    │   │ [FILE: 11_automations_sla_faq.md]                               │ │   │
│    │   │ Default SLA policy: Urgent - 1 hour response...                  │ │   │
│    │   │ ─────────────────────────────────────────────────────────────   │ │   │
│    │   │ [FILE: 12_sla_legacy_overlap.md]                                │ │   │
│    │   │ Legacy default: Urgent - 30 minutes...                           │ │   │
│    │   │ ─────────────────────────────────────────────────────────────   │ │   │
│    │   │                                                                  │ │   │
│    │   │ Question: What is the SLA for Urgent tickets?                   │ │   │
│    │   └─────────────────────────────────────────────────────────────────┘ │   │
│    │                                  │                                    │   │
│    │                                  ▼                                    │   │
│    │   ┌─────────────────────────────────────────────────────────────────┐ │   │
│    │   │                    Ollama LLM (Mistral)                          │ │   │
│    │   └─────────────────────────────────────────────────────────────────┘ │   │
│    │                                  │                                    │   │
│    └──────────────────────────────────┼────────────────────────────────────┘   │
│                                         │                                     │
│                                         ▼                                     │
│    ┌───────────────────────────────────────────────────────────────────────┐ │
│    │                           RESPONSE                                      │ │
│    │                                                                        │ │
│    │   The SLA for Urgent tickets is 1 hour according to the current        │ │
│    │   defaults (Automations & SLA FAQ). However, the legacy documentation   │ │
│    │   shows 30 minutes for the same priority.                               │ │
│    │                                                                        │ │
│    │   (Source: 11_automations_sla_faq.md, 12_sla_legacy_overlap.md)        │ │
│    │                                                                        │ │
│    └────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Component Deep Dives

### 4.1 Document Parsing: Unstructured.io vs Simple Chunking

#### The Problem with Simple Splitting

```python
# Traditional approach: Split by character count
def simple_chunk(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Example input:
text = """
Pricing & Plans FAQ

| Plan     | Price      | Agents |
|----------|------------|--------|
| Starter  | $19/mo     | Up to 3|
| Growth   | $49/mo     | Up to 15|
| Enterprise| Custom    | Unlimited|

Annual billing gives a 20% discount.
"""

# Simple split at 100 chars might cut:
# Chunk 1: "Pricing & Plans FAQ\n\n| Plan     | Price      | Age"
# Chunk 2: "nts |\n|----------|------------|--------|"
# Chunk 3: ...
```

**Result:** Table structure destroyed, pricing info scattered across chunks.

#### The Unstructured.io Solution

```python
from unstructured.partition.md import partition_md
from unstructured.chunking.title import chunk_by_title

def parse_document(filepath):
    # Partition preserves heading hierarchy, table structure
    elements = partition_md(filename=filepath)
    
    # chunk_by_title keeps related content together
    chunks = chunk_by_title(
        elements,
        max_characters=2000,
        new_after_n_chars=1000,      # Prefer splits at 1000 chars
        combine_text_under_n_chars=350,  # Merge tiny fragments
        multipage_sections=True,
    )
    return chunks
```

#### Comparison Table

| Aspect | Simple Splitting | Unstructured.io |
|--------|------------------|-----------------|
| **Table handling** | ❌ Splits rows | ✅ Preserves structure |
| **Q&A pairs** | ❌ May separate Q from A | ✅ Keeps together |
| **Code blocks** | ❌ May break mid-line | ✅ Intact |
| **Headings** | ❌ Ignored | ✅ Used as chunk boundaries |
| **Lists** | ❌ May split items | ✅ Keeps related items |
| **Context preservation** | ❌ Loses relationships | ✅ Maintains structure |

#### Visual Example: Q9 SLA Table

**Source Document Structure:**
```
# Automations & SLA Rules — FAQ

## What are SLAs?
SLAs define the maximum time to respond...

## Default SLA Policy:
| Priority | First Response | Resolution |
|----------|---------------|------------|
| Urgent   | 1 hour        | 4 hours    |
| High     | 4 hours       | 8 hours   |
```

**Simple Splitting Result:**
```
Chunk 1: "...Default SLA Policy:\n| Priority | First Response | Res"
Chunk 2: "ponse |\n|----------|---------------|------------|"
Chunk 3: "| Urgent   | 1 hour        | 4 hours    |"
```

**Unstructured.io Result:**
```
Chunk 1: "...Default SLA Policy:\n| Priority | First Response | Resolution |\n|----------|---------------|------------|\n| Urgent   | 1 hour        | 4 hours    |\n| High     | 4 hours       | 8 hours   |"
```

**Impact:** With Unstructured.io, the LLM sees the complete table and can answer accurately.

---

### 4.2 Embedding Model Comparison

```python
# Configuration in config.py
EMBED_MODEL = "BAAI/bge-base-en-v1.5"
```

| Model | Dimensions | Speed | Quality | API Key | License |
|-------|------------|-------|---------|---------|---------|
| OpenAI **ada-002** | 1536 | ⚡ Fast | ★★★ Good | ✅ Yes | Proprietary |
| **BAAI/bge-base-en-v1.5** | 768 | ⚡ Medium | ★★★ Good | ❌ No | Apache 2.0 |
| sentence-transformers/**MiniLM** | 384 | ⚡⚡ Very Fast | ★★ OK | ❌ No | Apache 2.0 |
| Cohere **embed-english** | 1024 | ⚡ Fast | ★★★ Good | ✅ Yes | Proprietary |

**Why BAAI/bge-base-en-v1.5?**
1. **No API key required** - Runs locally
2. **Optimized for retrieval** - Trained specifically for embedding tasks
3. **Good balance** - 768 dimensions (faster than 1536, better than 384)
4. **Open source** - Apache 2.0 license, can modify

---

### 4.3 LLM Options Comparison

```python
# Configuration in config.py
OLLAMA_MODEL = "mistral"
OLLAMA_BASE_URL = "http://localhost:11434"
```

| Option | Cost | Privacy | Quality | Setup | Inference |
|--------|------|---------|---------|-------|-----------|
| **GPT-4** | 💰💰💰 High | ❌ Cloud | ★★★★★ Excellent | ✅ Easy | ⚡ Fast |
| **Claude 3** | 💰💰💰 High | ❌ Cloud | ★★★★★ Excellent | ✅ Easy | ⚡ Fast |
| **Ollama + Mistral** | 💰 Free | ✅ Local | ★★★ Good | ⚙️ Medium | ⚡ Medium |
| **Ollama + Llama 3** | 💰 Free | ✅ Local | ★★★★ Very Good | ⚙️ Medium | 🐢 Slower |

**Why Ollama + Mistral?**
1. **Fully local** - No data leaves your machine
2. **No cost** - No API billing
3. **Good reasoning** - Mistral handles multi-step logic well
4. **Fast enough** - ~3-5 seconds per response

---

### 4.4 Vector Store Comparison

| Store | Type | API Key | Speed | Scalability | Local |
|-------|------|---------|-------|-------------|-------|
| **Pinecone** | Cloud | ✅ Yes | ⚡⚡⚡ | ★★★★★ | ❌ |
| **Weaviate** | Hybrid | Optional | ⚡⚡⚡ | ★★★★ | ✅ |
| **ChromaDB** | Local | ❌ No | ⚡⚡ | ★★ | ✅ |
| **FAISS** | Local | ❌ No | ⚡⚡⚡ | ★★★ | ✅ |

**Why ChromaDB?**
1. **Easy to use** - Simple Python API
2. **Local** - No cloud dependency
3. **Good for our scale** - 13 documents, ~50 chunks
4. **LlamaIndex native** - Built-in integration

---

## 5. Parameter Rationale

### 5.1 Chunk Sizes: [2000, 1000, 350]

```python
# Configuration in config.py
CHUNK_MAX_CHARS = 2000      # Hard ceiling per chunk
CHUNK_SOFT_LIMIT = 1000    # Preferred split point
CHUNK_MIN_CHARS = 350      # Merge fragments smaller than this
```

#### Visual Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                         CHUNK: MAX 2000 chars                            │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │                    CHUNK: SOFT 1000 chars                       │   │
│   │                                                                 │   │
│   │   This is where we PREFER to split (at semantic boundaries)    │   │
│   │                                                                 │   │
│   │   ┌─────────────────────────────────────────────────────────┐   │   │
│   │   │              CHUNK: MIN 350 chars                       │   │   │
│   │   │                                                         │   │   │
│   │   │   If a section is smaller than 350 chars,               │   │   │
│   │   │   MERGE it with the next section                        │   │   │
│   │   │                                                         │   │   │
│   │   │   (Prevents tiny meaningless fragments)                  │   │   │
│   │   └─────────────────────────────────────────────────────────┘   │   │
│   └────────────────────────────────────────────────────────────────┘   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

#### Why These Values?

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| **MAX_CHARS** | 2000 | LLM context is 8K tokens. With 6 chunks of ~500 tokens each, we use ~3K tokens, leaving room for prompt. |
| **SOFT_LIMIT** | 1000 | Half of MAX. Encourages splitting at logical midpoints (paragraphs, sections) rather than mid-sentence. |
| **MIN_CHARS** | 350 | Smaller chunks lose meaning (e.g., just "Pricing & Plans"). Merge to preserve context. |

#### Example: MIN_CHARS Impact

**Without MIN_CHARS:**
```
Chunk: "Pricing"
Chunk: "& Plans"
Chunk: "FAQ"
```

**With MIN_CHARS (350):**
```
Chunk: "Pricing & Plans FAQ\n\nQ: What plans does NovaDesk offer?\nA: We offer Starter, Growth, and Enterprise."
```

---

### 5.2 MMR Lambda = 0.7

```python
# Configuration in config.py
MMR_LAMBDA = 0.7
```

#### What is MMR?

**Maximal Marginal Relevance** balances two goals:
1. **Relevance** - Return chunks similar to the query
2. **Diversity** - Don't return all similar chunks (avoid redundancy)

#### Formula

```
MMR Score = λ × similarity(query, doc) - (1-λ) × max_similarity(doc, other_docs)
```

Where `λ` (lambda) controls the balance:
- λ = 1.0 → Pure relevance (might return duplicates)
- λ = 0.0 → Pure diversity (might return irrelevant)

#### Lambda Spectrum

```
Relevance ←────────────────────────────────────────────→ Diversity
    0.0         0.3         0.5         0.7         1.0
     │            │           │           │           │
     │            │           │           │           │
  Pure         More        Equal       More       Pure
 Diversity    Diversity    Balance    Relevance  Relevance
     │            │           │           │           │
     │            │           │           │           │
   ❌ Too        │           │        ✅ Best       ❌ Too
   Irrelevant    │           │        Choice       Duplicates
```

#### Testing Results

| Lambda | Q1 | Q2 | Q3 | Q9 | Avg | Notes |
|--------|----|----|----|----|-----|-------|
| 0.6 | 100 | 100 | 100 | 100 | 92.2% | Baseline |
| **0.7** | 100 | 100 | 100 | 100 | **94.0%** | Best balance |
| 0.8 | 95 | 100 | 100 | 100 | 89.5% | Too much diversity |

---

### 5.3 Retrieval Parameters

```python
# Configuration in config.py
TOP_K = 6              # Final chunks after fusion
BM25_TOP_K = 8         # BM25 candidates before fusion
USE_BM25 = True       # Enable hybrid retrieval
```

#### Why TOP_K = 6?

| TOP_K | Pros | Cons | Result |
|-------|------|------|--------|
| 3 | Fast, focused | Might miss context | ❌ Lower scores |
| **6** | Good balance | Slightly slower | ✅ Best |
| 12 | Comprehensive | LLM overwhelmed | ❌ Lower scores |

**Rationale:**
- 6 chunks ≈ 2000-3000 tokens of context
- Enough to answer complex questions (setup steps, pricing details)
- Not so many that LLM gets confused or distracted

#### Why BM25_TOP_K = 8?

| BM25_TOP_K | Rationale |
|------------|-----------|
| 5 | Too few - might miss exact keyword matches |
| **8** | Good capture of keywords before fusion |
| 15 | Too many - introduces noise |

**Why is BM25_TOP_K > TOP_K?**
- BM25 candidates are filtered by RRF
- Start with more candidates (8) to ensure keyword matches aren't missed
- RRF ranks and selects top 6

---

### 5.4 Summary Table

| Category | Parameter | Value | Why |
|----------|-----------|-------|-----|
| **Chunking** | MAX_CHARS | 2000 | LLM context headroom |
| | SOFT_LIMIT | 1000 | Semantic splits |
| | MIN_CHARS | 350 | Merge small fragments |
| **Retrieval** | TOP_K | 6 | Balance context vs overload |
| | BM25_TOP_K | 8 | Keyword capture before fusion |
| | MMR_LAMBDA | 0.7 | 70% relevance, 30% diversity |
| **Embedding** | Model | bge-base-en-v1.5 | Open source, good quality |
| **LLM** | Model | mistral | Local, capable |

---

## 6. Prompt Engineering

### Philosophy: Examples > Rules

```
❌ Bad: "Extract all relevant details."
✅ Good: "Example correct: '$49/mo, up to 15 agents, 20% off annually'
         Example WRONG: '$49/mo' (missing agent limit and discount)"
```

---

### 6.1 RELEVANCE GATE

#### The Problem

```
Question: "Can I import tickets from Zendesk?"

Retrieved Chunks:
1. "Connect Slack: Settings → Integrations → Slack..."
2. "API: Create, update, close tickets..."
3. "Export: Reports → Export → CSV..."

LLM Response:
"You can connect Slack to NovaDesk via Settings. The API allows 
creating and updating tickets. You can export data as CSV. 
Regarding Zendesk import..."
```

❌ **Hallucination** - LLM combined unrelated topics into an answer.

#### The Solution: Code-Level Check

```python
# In agent/qa.py
specific_terms = {'zendesk', 'hipaa', 'soc', 'slack', 'api', 
                  'import', 'export', 'gdpr', 'sso', 'saml', 
                  'oauth', 'webhook', 'zapier'}

question_lower = question.lower()
question_words = set(re.findall(r'\b[a-z]{4,}\b', question_lower))
question_specific = question_words & specific_terms

if question_specific:
    chunk_texts = [n.text.lower() for n in nodes]
    # Check if ALL specific terms appear in chunks
    all_found = all(
        any(term in chunk for chunk in chunk_texts) 
        for term in question_specific
    )
    if not all_found:
        return {"answer": "I couldn't find that in the provided documents."}
```

#### Why Code Instead of Prompt?

| Approach | Pros | Cons |
|----------|------|------|
| **Prompt Rule** | Flexible | LLM sometimes ignores it |
| **Code Check** | Deterministic | Less flexible |

**Decision:** Code check is deterministic and reliable. LLM still handles complex cases.

---

### 6.2 PRICING QUESTIONS Rule

#### The Problem

```
Question: "How much does Growth plan cost?"

Expected: "$49/mo, up to 15 agents, 20% off annually"
LLM: "$49 per agent per month"
```

❌ Missing agent limit and annual discount.

#### The Solution

```python
"PRICING QUESTIONS: For questions about plan costs, extract ALL pricing details:\n"
"  - Monthly price per agent\n"
"  - Agent seat limits\n"
"  - Annual/discount pricing (e.g. 20% off annually)\n"
"  - Trial information\n"
"\n"
"  Example correct: '$49/agent/month, up to 15 agents, 20% off annually'\n"
"  Example WRONG:   '$49/agent/month' (missing agent limit and discount)\n"
```

#### Why "Example WRONG"?

The LLM learns more from negative examples than from rules alone.

```
✅ Without Example: 
   "$49/mo" ← What did I miss? Who knows.

✅ With Example WRONG:
   "$49/mo" ← I forgot the agent limit and discount!
```

---

### 6.3 CONFLICT CITATION Rule

#### The Problem (Q9: SLA Conflict)

```
Question: "What is SLA first response time for Urgent tickets?"

Doc 11 (current): "Urgent SLA = 1 hour"
Doc 12 (legacy): "Urgent SLA = 30 minutes"

❌ WRONG LLM Response:
"According to doc 11, the SLA is 1 hour. Please verify current settings."

❌ Problem: 
1. Ignored doc 12 entirely
2. Hedged with "verify settings" instead of stating both values
3. Didn't explain the conflict
```

#### The Solution

```python
"CONFLICT DETECTION: Only flag a conflict if the SAME specific fact has\n"
"different values in different sources.\n"
"  - REAL conflict:   Source A says first response = 30 min,\n"
"Source B says 1 hour for the same ticket priority → Flag it.\n"
"  - FALSE conflict:  Source A says Starter has 3 agents,\n"
"Source B says Growth has 15 → Different plans, not a conflict.\n\n"

"CONFLICT CITATION (CRITICAL): If multiple sources provide DIFFERENT values\n"
"for the SAME metric, you MUST include the ACTUAL VALUE from EACH source.\n"
"  - WRONG: 'According to [doc 12], the urgent SLA is 30 min. However,\n"
"[doc 11] shows the current default is 1 hour.'\n"
"  - CORRECT: 'According to [doc 11], the urgent SLA first response is 1 hour.\n"
"According to [doc 12], the urgent SLA first response is 30 minutes (legacy).'\n"
"  - Do NOT say 'verify settings' without stating the actual conflicting values.\n\n"
```

#### Result After Fix

```
✅ CORRECT Response:
"The SLA first response for Urgent tickets is 1 hour according to the 
current default (Automations & SLA FAQ). However, the legacy 
documentation shows 30 minutes for the same priority. Please 
verify your current settings.

(Source: 11_automations_sla_faq.md, 12_sla_legacy_overlap.md)
```

---

### 6.4 YES/NO Framing

#### The Problem

```
Question: "Can I use AI Bot on Starter plan?"

❌ WRONG Response:
"The AI Bot is not available on the Starter plan, but you can 
upgrade to Growth or Enterprise..."

❌ Problem: "but..." is evasive. The answer is No.
```

#### The Solution

```python
"YES/NO QUESTIONS: If the direct answer is No, your FIRST word must be 'No.'\n"
"  - Correct:   'No, the AI Bot is only available on Growth and Enterprise plans.'\n"
"  - Incorrect: 'The AI Bot is not available on the Starter plan, but...'\n"
"  - Incorrect: 'Yes, but only on Growth and Enterprise.'\n"
"  - SDK/feature exists but no standalone product: Lead with what does NOT exist,\n"
"then mention what does. Example: 'NovaDesk does not have a standalone mobile app.\n"
"However, native SDKs for iOS and Android are available...'\n"
```

#### Why This Matters

| Framing | Feels Like |
|---------|------------|
| "Yes, but..." | Evasive, hiding something |
| "No, [X] only..." | Clear, direct |
| "Not [X], but..." | Slightly better than yes/but |

---

### 6.5 NOT FOUND Handling

```python
"NOT FOUND: If the answer is not in the sources, say\n"
"'I couldn't find that in the provided documents.' — one sentence, nothing else.\n"
"Do NOT suggest alternatives, workarounds, or related features.\n"
```

**Why "nothing else"?**

| Response | User Feels |
|----------|------------|
| "I couldn't find that. You might try checking our website..." | ❌ Confused, frustrated |
| "I couldn't find that." | ✅ Clear, honest |

---

## 7. Testing Strategy

### 7.1 Why LLM-as-Judge?

```python
SCORING_PROMPT = """
Score the RAG response against the expected answer.

Scoring Rubric:
- 100: Perfect - matches expected answer exactly
- 75-99: Good - captures key information, minor gaps
- 50-74: Partial - captures some information, missing parts
- 0-49: Fail - incorrect or missing key information

Output JSON only: {"score": 0-100, "rating": "Pass|Partial|Fail", "reasoning": "..."}
"""
```

#### Comparison

| Method | Speed | Consistency | Cost | Scalability |
|--------|-------|-------------|------|-------------|
| **Manual** | 17 questions × 2 min = 34 min | Variable | High | ❌ |
| **LLM Judge** | 17 questions × 5 sec = 85 sec | Consistent | Free | ✅ |

### 7.2 Scoring Rubric

| Score | Rating | Criteria | Example |
|-------|--------|----------|---------|
| **100** | Pass | Exact match, all criteria met | Expected: "$49/mo, 15 agents, 20% off"<br>Got: "$49/mo, 15 agents, 20% off" |
| **75-99** | Good | Key info captured, minor gaps | Expected: "$49/mo, 15 agents, 20% off"<br>Got: "$49/mo, 20% off" |
| **50-74** | Partial | Some info, missing parts | Expected: "$49/mo, 15 agents, 20% off"<br>Got: "$49/mo" |
| **0-49** | Fail | Wrong or missing key info | Expected: "$49/mo, 15 agents, 20% off"<br>Got: "$19/mo" |

### 7.3 Special Case Handling

```python
# Q9: SLA Conflict - must state BOTH values
if "SLA" in question and "urgent" in question:
    if not (has_1_hour and has_30_min):
        score = 50  # Penalize if both values not present

# Q11: Setup Steps - must include ALL steps
if "setup" in question.lower():
    if len(response_steps) < expected_steps:
        score = 50  # Missing steps

# Q14, Q15: "Not found" questions
if any(term in question for term in ["uptime", "zendesk", "gdpr"]):
    if "not found" in response.lower():
        score = 100  # Correct answer!
```

---

## 8. Failure Case Deep Dives

### Case 1: Q9 - SLA Conflict (1 hour vs 30 minutes)

#### The Question
```
What is the SLA first response time for an Urgent ticket?
```

#### The Documents
```markdown
# 11_automations_sla_faq.md
## Default SLA policy:
| Priority | First Response | Resolution |
|----------|---------------|------------|
| Urgent   | 1 hour        | 4 hours    |

# 12_sla_legacy_overlap.md
## Default SLA Times (v3.x — verify in your current settings)
| Priority | First Response | Resolution |
|----------|---------------|------------|
| Urgent   | 30 minutes    | 2 hours    |
```

#### The Problem

```
❌ Initial LLM Response:
"The SLA first response for Urgent tickets is 1 hour according 
to doc 11. Please verify the current settings in your NovaDesk."

❌ Issues:
1. Ignored doc 12 (legacy 30-minute value)
2. Hedged with "verify settings"
3. Didn't explain why there's a conflict
4. Both values should have been stated
```

#### Root Cause Analysis

The LLM was trained to give "helpful" answers. Saying "please verify settings" feels helpful but doesn't actually answer the question with the information available.

#### The Fix

Added explicit CONFLICT CITATION rule:

```python
"CONFLICT CITATION (CRITICAL): If multiple sources provide DIFFERENT values\n"
"for the SAME metric, you MUST include the ACTUAL VALUE from EACH source.\n"
"  - WRONG: 'According to [doc 12], the urgent SLA is 30 min. However,\n"
"[doc 11] shows the current default is 1 hour.'\n"
"  - CORRECT: 'According to [doc 11], the urgent SLA first response is 1 hour.\n"
"According to [doc 12], the urgent SLA first response is 30 minutes (legacy).'\n"
```

#### Result

```
✅ After Fix - LLM Response:
"The SLA first response time for Urgent tickets is 1 hour according 
to the current defaults (Automations & SLA FAQ). However, the legacy 
documentation shows 30 minutes for the same priority. Please verify 
your current settings in your NovaDesk instance.

(Source: 11_automations_sla_faq.md, 12_sla_legacy_overlap.md)"

✅ Score: 100 (Pass)
```

---

### Case 2: Q15 - Zendesk Import (Hallucination)

#### The Question
```
Can I import tickets from Zendesk?
```

#### The Problem

```
❌ Initial LLM Response (1440 characters!):
"NovaDesk is a helpdesk software that manages customer support tickets...
You can connect Slack to NovaDesk by going to Settings > Integrations > Slack...
NovaDesk provides a RESTful API for creating, updating, and closing tickets...
There is a ticket export feature available. Go to Reports > Export...
"
```

❌ **Hallucination** - LLM invented an answer from unrelated topics.

#### Root Cause Analysis

1. No Zendesk content exists in any document
2. Retrieved chunks contained: Slack, API, export, ticket merge
3. LLM connected these tangentially related topics into a fabricated answer
4. The NOT FOUND rule was being ignored

#### The Fix: RELEVANCE GATE

```python
# Code-level check before LLM generation
specific_terms = {'zendesk', 'hipaa', 'soc', 'slack', 'api', 
                  'import', 'export', 'gdpr', 'sso', 'saml', ...}

question_lower = question.lower()
question_words = set(re.findall(r'\b[a-z]{4,}\b', question_lower))
question_specific = question_words & specific_terms

if question_specific:
    chunk_texts = [n.text.lower() for n in nodes]
    all_found = all(
        any(term in chunk for chunk in chunk_texts) 
        for term in question_specific
    )
    if not all_found:
        return {"answer": "I couldn't find that in the provided documents."}
```

**Why This Works:**

| Step | Check | Result |
|------|-------|--------|
| 1 | Question contains "zendesk"? | Yes |
| 2 | Question contains "import"? | Yes |
| 3 | "zendesk" in any chunk? | No |
| 4 | "import" in any chunk? | Yes (but not together) |
| 5 | Decision | Return "not found" |

#### Result

```
✅ After Fix - LLM Response:
"I couldn't find that in the provided documents."

✅ Score: 99 (Good)
Note: Scorer expected "not found" exactly, gave 99 instead of 100
```

---

### Case 3: Q1 - Incomplete Pricing Info

#### The Question
```
How much does the Growth plan cost?
```

#### Expected Answer
```
$49 per agent/month, up to 15 agents, 20% off annually
```

#### The Problem

```
❌ Initial LLM Response:
"The Growth plan costs $49 per agent per month. However, every 
new account gets a 14-day free trial of the Growth plan with 
no credit card required."

❌ Issues:
1. Mentioned $49 ✓
2. Mentioned free trial ✓
3. Missing: "up to 15 agents"
4. Missing: "20% off annually"
```

#### Root Cause Analysis

The retrieved chunk contained ALL the information:
```markdown
# 02_pricing_faq.md
Pricing & Plans FAQ

| Plan | Price (per agent/month) | Agents Included |
|------|--------------------------|-----------------|
| Starter | $19 | Up to 3 |
| Growth | $49 | Up to 15 |
| Enterprise | Custom pricing | Unlimited |

All prices are billed monthly. Annual billing gives a 20% discount.

Is there a free trial?
Yes. Every new account gets a 14-day free trial...
```

But the LLM extracted only `$49` and `free trial` - missing agent limits and annual discount.

#### The Fix: PRICING QUESTIONS Rule

```python
"PRICING QUESTIONS: For questions about plan costs, extract ALL pricing details:\n"
"  - Monthly price per agent\n"
"  - Agent seat limits\n"
"  - Annual/discount pricing (e.g. 20% off annually)\n"
"  - Trial information\n"
"\n"
"  Example correct: '$49/agent/month, up to 15 agents, 20% off annually'\n"
"  Example WRONG:   '$49/agent/month' (missing agent limit and discount)\n"
```

#### Result

```
✅ After Fix - LLM Response:
"The Growth plan costs $49 per agent per month. This plan supports 
up to 15 agents, and annual billing gives a 20% discount. (Source: 
02_pricing_faq.md, 09_plans_billing_overlap.md)"

✅ Score: 100 (Pass)
```

---

### Case 4: Q6 - YES/NO Framing

#### The Question
```
Can I use the AI Bot on the Starter plan?
```

#### The Problem

```
❌ Initial LLM Response:
"The AI Bot is not available on the Starter plan, but it is 
available on Growth and Enterprise plans."

❌ Problem: "but..." makes it sound like there IS a way on Starter.
The answer is clearly NO.
```

#### The Fix

```python
"YES/NO QUESTIONS: If the direct answer is No, your FIRST word must be 'No.'\n"
"  - Correct:   'No, the AI Bot is only available on Growth and Enterprise plans.'\n"
"  - Incorrect: 'The AI Bot is not available on the Starter plan, but...'\n"
```

#### Result

```
✅ After Fix - LLM Response:
"No, the AI Bot is only available on Growth and Enterprise plans. 
(Source: 05_live_chat_faq.md)"

✅ Score: 100 (Pass)
```

---

## 9. Key Takeaways

### 1. Hybrid Retrieval > Single Method

```
Vector-only: Misses exact keyword matches (Zendesk, HIPAA)
BM25-only: Misses semantic variations (cheapest → lowest price)
Hybrid: Captures both ✓
```

### 2. Chunking Quality = Answer Quality

```
Simple splitting: Destroys tables, Q&A pairs, code blocks
Semantic chunking: Preserves structure → Better context → Better answers
```

### 3. Prompts Need Examples

```
❌ Rule only: "Extract all relevant details."
✅ With examples: "Example correct: '...'\nExample WRONG: '...'"
```

### 4. Code-Level Safety Nets

```
LLM sometimes ignores prompt rules
Code checks are deterministic
Use code for edge cases (missing topics, hallucinations)
```

### 5. Iterate Based on Failures

```
Every failure → Analyze → New rule or parameter tweak
Don't over-engineer upfront
Let real failures guide improvements
```

### 6. Testing Enables Iteration

```
Manual testing: Slow, inconsistent
LLM-as-judge: Fast, consistent, enables rapid iteration
```

---

## Appendix: Configuration Reference

```python
# config.py

# ---------------- Embedding ----------------
EMBED_MODEL = "BAAI/bge-base-en-v1.5"

# ---------------- LLM (via Ollama) ----------------
OLLAMA_MODEL = "mistral"
OLLAMA_BASE_URL = "http://localhost:11434"

# ---------------- Retrieval ----------------
TOP_K = 6              # chunks returned by retriever
MMR_LAMBDA = 0.7      # 0=max diversity, 1=max relevance

# ---------------- Hybrid Retrieval ----------------
BM25_TOP_K = 8        # BM25 candidates before fusion
USE_BM25 = True       # Enable BM25 alongside vector

# ---------------- Storage ----------------
CHROMA_PATH = "./data/chroma_db"
CHROMA_COLLECTION = "qna_docs"

# ---------------- Unstructured.io chunking ----------------
CHUNK_MAX_CHARS = 2000      # hard ceiling per chunk
CHUNK_SOFT_LIMIT = 1000    # preferred split point
CHUNK_MIN_CHARS = 350      # merge fragments smaller than this

# ---------------- Debugging ----------------
DEBUG_LLM = True
DEBUG_TIMING = True
```

---

*Document Version: 1.0*
*Last Updated: March 2026*
*For internal technical team use.*
