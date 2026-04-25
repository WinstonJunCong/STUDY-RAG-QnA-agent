# Session Memory Q&A Agent

A RAG-powered Q&A system with persistent session memory. Answers questions using a knowledge base while retaining context across conversation turns.

## Features

- **Session Memory**: Hybrid memory combining recent message buffer + semantic search
- **RAG Retrieval**: Vector search with MMR (Maximal Marginal Relevance)
- **Google GenAI**: Gemini 3.1 Flash Lite for LLM, Gemini Embedding 001 for embeddings

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | LlamaIndex |
| Vector DB | ChromaDB |
| Embeddings | Google GenAI (gemini-embedding-001) |
| LLM | Google GenAI (gemini-3.1-flash-lite-preview) |
| Memory | Hybrid (in-memory buffer + ChromaDB semantic search) |

---

## Project Structure

```
├── src/
│   ├── agent/              # qa.py, memory.py
│   ├── ingest/            # text_loader.py
│   └── pipeline/         # index_builder.py
├── data/
│   ├── input/            # Source documents
│   └── chroma_db/        # Vector index (auto-created)
├── config.py
├── ingestion.py
├── query.py
└── requirements.txt
```

---

## Quick Start

### Prerequisites

1. **Google API Key**
   ```bash
   export GOOGLE_API_KEY="your-api-key-here"
   ```

2. **Python dependencies (recommend a venv)**
   ```bash
   pip install -r requirements.txt
   ```

### Ingest Documents

```bash
python ingestion.py
```

### Ask Questions

```bash
python query.py
```

---

## Architecture

### Query Pipeline

```
User Question → [Memory Retrieval] → [RAG Retrieval] → LLM → Answer
```

1. **Memory Retrieval**: Recent buffer (last 5) + semantic search on conversation history
2. **RAG Retrieval**: Vector search with MMR against knowledge base
3. **LLM Generation**: Combines memory context + document context to generate answer

### Vector Retrieval with MMR

Uses Maximal Marginal Relevance for result diversity:

- **Vector search**: Captures semantic similarity ("cheapest" → "lowest price")
- **MMR**: Balances relevance with diversity, avoiding redundant results

### Session Memory

Hybrid memory combining two retrieval strategies:

**1. Recent Buffer** (guaranteed recency)
- Last 5 messages stored in-memory
- Always included in context, regardless of query
- Ensures the LLM never loses immediate conversation thread

**2. Semantic Search** (relevant context)
- All messages stored in ChromaDB
- Vector similarity retrieves past context relevant to current query
- Skipped if already covered by recent buffer (deduplication)

```
Memory Context = Recent Buffer (last 5) + Semantic Search (if not covered)
```

---

## Configuration

All settings in `config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `TOP_K` | 6 | Chunks returned by retriever |
| `MMR_LAMBDA` | 0.7 | 0=max diversity, 1=max relevance |
| `MEMORY_TOP_K` | 4 | Semantic search results for memory retrieval |
| `MEMORY_RECENT_COUNT` | 5 | Recent messages to always include in context |

---

## Document Sources

Add documents to `data/input/` directory (`.txt` and `.md` supported).

---

## Troubleshooting

**"GOOGLE_API_KEY not set"**
```bash
export GOOGLE_API_KEY="your-api-key"
```

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**Poor answer quality**
Check `config.py` for tuning options.