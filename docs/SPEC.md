# NovaDesk RAG Agent - Technical Specification

**Version:** R12b  
**Last Updated:** March 2026  
**Status:** Active Development

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INGESTION PIPELINE                               │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐     ┌─────────────────────┐     ┌────────────────────────┐
  │ sample_files  │ ──▶ │  Unstructured.io   │ ──▶ │  chunk_by_title       │
  │   (.md)      │     │  partition_md      │     │  (1500/1000/350)      │
  └──────────────┘     └─────────────────────┘     └────────────────────────┘
                                                              │
                    ┌──────────────────────────────────────────┘
                    ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                           OUTPUTS                                        │
  ├──────────────────────────────┬──────────────────────────────────────────┤
  │  ChromaDB (chroma_db/)       │  BM25 Nodes (bm25_nodes.json)           │
  │  - 54 vector embeddings     │  - 54 raw text nodes                     │
  │  - 768-dim BAAI/bge         │  - For keyword-based retrieval           │
  └──────────────────────────────┴──────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            RETRIEVAL PIPELINE                              │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │   Question   │ ──┐
  └──────────────┘   │
                     ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                       HYBRID RETRIEVAL (Parallel)                        │
  ├─────────────────────────────────────────────────────────────────────────┤
  │  ┌─────────────────────────┐    ┌─────────────────────────────────┐   │
  │  │  Vector Retriever       │    │  BM25 Retriever                 │   │
  │  │  - ChromaDB             │    │  - bm25_nodes.json              │   │
  │  │  - TOP_K = 6           │    │  - BM25_TOP_K = 8              │   │
  │  │  - MMR λ = 0.7         │    │  - Keyword matching             │   │
  │  └─────────────────────────┘    └─────────────────────────────────┘   │
  │              │                              │                             │
  └──────────────┼──────────────────────────────┼─────────────────────────────┘
                 │                              │
                 ▼                              ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                   QueryFusionRetriever (RRF)                            │
  │  - Combines rankings from vector + BM25                               │
  │  - similarity_top_k = 6                                              │
  │  - mode = "reciprocal_rerank"                                       │
  │  - num_queries = 1 (no multi-query expansion)                        │
  └─────────────────────────────────────────────────────────────────────────┘
                 │
                 ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         LLM GENERATION                                  │
  │  - Ollama (mistral)                                                   │
  │  - QA_PROMPT with conflict detection rules                             │
  └─────────────────────────────────────────────────────────────────────────┘
```

---

## Configuration

### config.py

```python
# ---------------- Embedding ----------------
EMBED_MODEL = "BAAI/bge-base-en-v1.5"

# ---------------- LLM (via Ollama) ----------------
OLLAMA_MODEL = "mistral"
OLLAMA_BASE_URL = "http://localhost:11434"

# ---------------- Retrieval ----------------
TOP_K = 6              # Final chunks after fusion
MMR_LAMBDA = 0.7      # Relevance vs diversity (0=max diversity, 1=max relevance)

# ---------------- Hybrid Retrieval ----------------
BM25_TOP_K = 8        # BM25 candidates before fusion
USE_BM25 = True       # Enable BM25 alongside vector search

# ---------------- Storage ----------------
CHROMA_PATH = "./chroma_db"
CHROMA_COLLECTION = "qna_docs"

# ---------------- Unstructured.io chunking params ----------------
CHUNK_MAX_CHARS = 2000      # Hard ceiling per chunk
CHUNK_SOFT_LIMIT = 1000    # Preferred split point
CHUNK_MIN_CHARS = 350       # Merge sections smaller than this

# ---------------- Debugging ----------------
DEBUG_LLM = True
DEBUG_TIMING = True
```

---

## Document Processing

### Chunking Strategy

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `CHUNK_MAX_CHARS` | 2000 | Hard ceiling - prevents oversized chunks |
| `CHUNK_SOFT_LIMIT` | 1000 | Preferred split point for cleaner boundaries |
| `CHUNK_MIN_CHARS` | 350 | Minimum size before merging with previous |

### Parser: Unstructured.io

- Uses `partition_md()` for markdown files
- Uses `chunk_by_title()` to keep Q&A pairs together
- Preserves semantic boundaries (headers, tables, lists)

### Index Stats

| Metric | Value |
|--------|-------|
| Total Documents | 13 |
| Total Chunks | 54 |
| ChromaDB Nodes | 54 |
| BM25 Nodes | 54 |
| Embedding Model | BAAI/bge-base-en-v1.5 (768-dim) |

---

## Retrieval Pipeline

### 1. Vector Retriever (ChromaDB)

```python
index.as_retriever(
    vector_store_query_mode="mmr",
    similarity_top_k=6,
    vector_store_kwargs={"mmr_threshold": 0.7},
)
```

### 2. BM25 Retriever

```python
BM25Retriever.from_defaults(
    nodes=loaded_from_bm25_nodes_json,
    similarity_top_k=8,
)
```

### 3. QueryFusionRetriever (Reciprocal Rank Fusion)

```python
QueryFusionRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    similarity_top_k=6,
    num_queries=1,
    mode="reciprocal_rerank",
    use_async=False,
)
```

---

## Prompt Template (QA_PROMPT)

### Key Rules

1. **RELEVANCE FILTER** - Only use chunks that directly answer the question
2. **COMPLETENESS** - Combine info from multiple sources without repetition
3. **SCOPE** - Answer exactly what was asked
4. **FORMAT** - Plain paragraphs, numbered lists only when needed
5. **NOT FOUND** - One sentence, no suggestions
6. **YES/NO QUESTIONS** - "No" must be first word
7. **CONFLICT DETECTION** - Flag only same-fact conflicts, not different-topic conflicts
8. **CONFLICT CITATION (CRITICAL)** - State ACTUAL values from EACH source

### Conflict Citation Example

```python
"CONFLICT CITATION (CRITICAL): If multiple sources provide DIFFERENT values 
for the SAME metric, you MUST include the ACTUAL VALUE from EACH source.

WRONG: 'According to [doc 12], the urgent SLA is 30 min. However, 
[doc 11] shows the current default is 1 hour.'

CORRECT: 'According to [doc 11], the urgent SLA first response is 1 hour. 
According to [doc 12], the urgent SLA first response is 30 minutes (legacy).'
```

---

## File Structure

```
chat_agent/
├── config.py                    # All configuration
├── ingestion.py                # Entry point for ingestion
├── query.py                   # Interactive Q&A CLI
├── run_uat.py                  # Batch UAT testing
│
├── pipeline/
│   └── index_builder.py       # Index building with Unstructured.io
│
├── agent/
│   └── qa.py                 # Q&A retrieval + generation
│
├── ingest/
│   ├── text_loader.py         # Markdown/text loading
│   ├── html_loader.py         # Web scraping (optional)
│   └── video_loader.py        # Video transcription (optional)
│
├── sample_files/              # Source documents (13 .md files)
│   ├── 01_product_overview.md
│   ├── 02_pricing_faq.md
│   ├── 03_getting_started.md
│   ├── 04_ticketing_faq.md
│   ├── 05_live_chat_faq.md
│   ├── 06_integrations_api_faq.md
│   ├── 07_security_compliance_faq.md
│   ├── 08_knowledge_base_faq.md
│   ├── 09_plans_billing_overlap.md
│   ├── 10_quick_setup_checklist_overlap.md
│   ├── 11_automations_sla_faq.md
│   ├── 12_sla_legacy_overlap.md
│   └── 13_account_admin_faq.md
│
├── chroma_db/                 # Persisted vector index (ChromaDB)
└── bm25_nodes.json           # Persisted nodes for BM25 (JSON)
```

---

## Dependencies

```
# Core framework
llama-index>=0.10.0
llama-index-vector-stores-chroma>=0.1.0

# BM25 + Reciprocal Rank Fusion
llama-index-retrievers-bm25>=0.1.0
rank-bm25>=0.2.0

# Embeddings
llama-index-embeddings-huggingface>=0.2.0
sentence-transformers>=2.7.0

# LLM
llama-index-llms-ollama>=0.1.0

# Vector store
chromadb>=0.5.0

# Document parsing
beautifulsoup4>=4.12.0
requests>=2.31.0

# Unstructured.io
unstructured>=0.10.0
unstructured[md]>=0.10.0

# Utilities
python-dotenv>=1.0.0
rich>=13.0.0
psutil>=5.9.0
openpyxl>=1.0.0
pandas>=1.5.0
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| R9 | Mar 2026 | MarkdownNodeParser, no AutoMerging |
| R10 | Mar 2026 | Unstructured.io migration |
| R10b | Mar 2026 | MMR lambda = 0.7 |
| R10c | Mar 2026 | Prompt tuning |
| R11 | Mar 2026 | BM25 hybrid retrieval added |
| R11b | Mar 2026 | Chunk size fix (2000/1000/350) |
| R12 | Mar 2026 | Conflict detection prompt |
| R12b | Mar 2026 | Stronger conflict citation rule |

---

## Key Decisions

### Why Unstructured.io?

- Better table handling than MarkdownNodeParser
- Preserves heading hierarchy as metadata
- Automatically handles .md, .txt, .pdf, .html, .docx

### Why BM25 + Vector?

- Vector search: Semantic similarity
- BM25: Exact keyword matching
- Combined: Best of both worlds

### Why No AutoMerging?

- Previous versions with AutoMerging had false conflict hallucinations
- Flat chunking with Unstructured.io keeps Q&A pairs together
- Simpler pipeline, fewer config knobs

---

## Running the Pipeline

### Ingest Documents
```bash
.venv\Scripts\python.exe ingestion.py
```

### Interactive Query
```bash
.venv\Scripts\python.exe query.py
```

### Run UAT
```bash
.venv\Scripts\python.exe run_uat.py
```

---

## Git Branches

| Branch | Description |
|--------|-------------|
| main | Current development |
| R9-markdown-backup | Backup of R9 (MarkdownNodeParser version) |

---

*This specification reflects the current R12b pipeline state.*
