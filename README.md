# 📚 NovaDesk Q&A RAG System

A production-ready Retrieval-Augmented Generation (RAG) system for answering customer questions about NovaDesk using company documentation.

## Performance

| Metric | Score |
|--------|-------|
| UAT Pass Rate | 14/17 (82%) |
| Average Score | **94.0%** |
| Response Time | ~3-5 seconds |

## Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Framework | LlamaIndex | Best Python RAG library |
| Vector DB | ChromaDB | Local, fast, easy |
| Embeddings | BAAI/bge-base-en-v1.5 | Open-source, good quality |
| LLM | Ollama + Mistral | Fully local, private |
| Parsing | Unstructured.io | Semantic document understanding |
| Retrieval | Hybrid (Vector + BM25 + RRF) | Captures semantic and exact matches |

No API keys required. Runs entirely on local hardware.

---

## Project Structure

```
chat_agent/
├── agent/
│   └── qa.py                 # Hybrid retrieval + LLM generation
├── data/
│   ├── chroma_db/            # Vector index (auto-created)
│   └── bm25_nodes.json       # BM25 corpus (auto-created)
├── docs/
│   ├── PRESENTATION_NOTES.md  # Technical deep dive
│   └── ITERATION_HISTORY.md  # Version history
├── ingest/
│   ├── text_loader.py         # .txt / .md files
│   ├── html_loader.py         # Web scraping
│   └── video_loader.py        # Whisper transcription
├── pipeline/
│   └── index_builder.py       # Unstructured.io + ChromaDB indexing
├── scoring/
│   └── score_responses.py      # LLM-judged evaluation
├── sample_files/               # 13 source markdown documents
├── config.py                  # All configuration settings
├── ingestion.py               # Document ingestion entry point
├── query.py                  # Interactive Q&A CLI
├── run_uat.py                # Automated UAT testing
└── requirements.txt
```

---

## Quick Start

### Prerequisites

1. **Ollama** installed and running
   ```bash
   ollama pull mistral
   ollama serve
   ```

2. **Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Ingest Documents (One-time)

```bash
python ingestion.py
```

This will:
1. Load documents from `sample_files/`
2. Parse with Unstructured.io (semantic chunking)
3. Build hybrid index (ChromaDB + BM25)
4. Save to `./data/`

### Ask Questions

```bash
python query.py
```

### Run UAT Tests

```bash
python run_uat.py
```

---

## Configuration

All settings in `config.py`:

### Retrieval Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TOP_K` | 6 | Final chunks after fusion |
| `MMR_LAMBDA` | 0.7 | 0=max diversity, 1=max relevance |
| `BM25_TOP_K` | 8 | BM25 candidates before fusion |
| `USE_BM25` | True | Enable hybrid retrieval |

### Chunking Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CHUNK_MAX_CHARS` | 2000 | Hard ceiling per chunk |
| `CHUNK_SOFT_LIMIT` | 1000 | Preferred split point |
| `CHUNK_MIN_CHARS` | 350 | Merge smaller fragments |

### Models

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EMBED_MODEL` | BAAI/bge-base-en-v1.5 | Embedding model |
| `OLLAMA_MODEL` | mistral | LLM model |

---

## Architecture Highlights

### Hybrid Retrieval

Combines vector search with BM25 using Reciprocal Rank Fusion:

```
Query → [Vector Search + MMR] → [BM25 Search] → RRF Fusion → Top-K Chunks
```

- **Vector search**: Captures semantic similarity ("cheapest" → "lowest price")
- **BM25**: Captures exact keywords ("Zendesk", "HIPAA")
- **RRF**: Combines both rankings

### Semantic Chunking

Uses Unstructured.io for intelligent document parsing:

- Preserves table structure
- Keeps Q&A pairs together
- Respects heading hierarchy

### Prompt Engineering

Comprehensive rules for consistent, accurate answers:

- **RELEVANCE GATE**: Prevents hallucination on missing topics
- **PRICING QUESTIONS**: Extracts all pricing details
- **CONFLICT CITATION**: States actual values from conflicting sources
- **YES/NO FRAMING**: Clear direct answers

---

## Testing

### UAT Test Suite

17 questions covering:
- Pricing (plans, discounts)
- Setup (account, channels)
- Features (AI Bot, Knowledge Base)
- Compliance (SOC 2, HIPAA)
- Integrations (Slack, API)

### Scoring

LLM-judged evaluation with rubric:
- **100 (Pass)**: Exact match
- **75-99 (Good)**: Minor gaps
- **50-74 (Partial)**: Missing parts
- **0-49 (Fail)**: Wrong or missing

---

## Documentation

| Document | Purpose |
|----------|---------|
| `docs/PRESENTATION_NOTES.md` | Technical deep dive with diagrams and code |
| `docs/ITERATION_HISTORY.md` | Version-by-version development history |
| `docs/SPEC.md` | Technical specification |

---

## Cost Breakdown

| Component | Cost |
|-----------|------|
| Embeddings (HuggingFace) | ✅ Free |
| LLM (Ollama) | ✅ Free |
| Vector DB (ChromaDB) | ✅ Free |
| Document parsing (Unstructured.io) | ✅ Free |
| **Total** | **$0** |

---

## Troubleshooting

**"Connection refused" from Ollama**
→ Make sure Ollama is running: `ollama serve`

**Slow embedding on first run**
→ Normal — HuggingFace downloads the model once, then it's cached.

**Poor answer quality**
→ Check `config.py` for tuning options, or review `docs/PRESENTATION_NOTES.md`

**"Module not found" errors**
→ Run `pip install -r requirements.txt`

---

## Version History

See `docs/ITERATION_HISTORY.md` for detailed version-by-version breakdown.

| Version | Key Change | Score |
|---------|------------|-------|
| R10 | Unstructured.io migration | 95.5% |
| R12b | Conflict citation rules | 94.1% |
| R13/14 | RELEVANCE GATE | 94.0% |

---

*Last Updated: March 2026*
