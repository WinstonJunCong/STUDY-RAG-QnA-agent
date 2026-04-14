# Implementation Plan: CLI to API Transformation

## Overview

Transform the current CLI-based RAG system into a FastAPI microservice for a 3D animation studio knowledge base.

## Domain

Documents about:
- DCC tools (Maya, Blender, 3ds Max, Motion Builder, Unreal)
- AI tools and addons
- Training materials
- Studio workflow documentation

## Configuration

| Config | Value | Notes |
|--------|-------|-------|
| `EMBED_MODEL` | Octen-8B | Local embedding model |
| `OLLAMA_MODEL` | mistral | Local LLM |
| `TEXT_FOLDERS` | `./.input` | Document source |
| `FAQ_FILE` | `data/faq_entries.md` | Human-approved FAQs (Markdown) |
| `FAQ_DRAFTS_FILE` | `data/faq_drafts.md` | Generated drafts (pending review) |
| `SIMILARITY_THRESHOLD` | `0.9` | Query deduplication |
| `MIN_QUERY_COUNT` | `3` | Min queries to trigger FAQ generation |
| `FAQ_SCHEDULE` | `biweekly` | Every 2 weeks |

---

## Phased Implementation

### Phase 1: Core API (Priority)

**Goal**: FastAPI server with query cache, SQLite logger, full CRUD endpoints

**Deliverables**:
- FastAPI application with all endpoints
- Refactored `RAGService` class
- Query cache layer (exact + semantic match)
- SQLite query logger

**API Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/query` | POST | Ask question (logs + cache-check + LLM) |
| `/ingest` | POST | Rebuild index |
| `/index/status` | GET | Index stats |
| `/index` | DELETE | Clear index |
| `/faq` | GET | List approved FAQs |
| `/faq/drafts` | GET | List draft FAQs |
| `/faq/generate` | POST | Generate drafts from queries |
| `/faq/approve` | POST | Approve drafts, re-ingest |
| `/cache/clear` | DELETE | Clear query cache |

### Phase 2: FAQ Auto-Enhancement

**Goal**: Bi-weekly FAQ generation with human review workflow

**Deliverables**:
- Query clustering (semantic similarity > 0.9, count >= 3)
- FAQ draft generation from indexed documents
- Human review workflow (markdown files)
- Bi-weekly scheduler
- `/faq/approve` → re-ingest pipeline

---

## File Structure

```
chat_agent/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── models.py            # Pydantic schemas
│   └── routes/
│       ├── __init__.py
│       ├── query.py         # /query (cache-first)
│       ├── ingest.py        # /ingest
│       ├── index.py         # /index/*
│       └── faq.py           # /faq/*
├── services/
│   ├── __init__.py
│   ├── rag_service.py       # Core RAG service
│   ├── query_logger.py      # SQLite query log
│   ├── cache.py             # Exact + semantic cache
│   ├── faq_generator.py    # FAQ draft generation
│   └── scheduler.py        # Bi-weekly scheduler
├── data/
│   ├── query_log.db         # SQLite (auto-created)
│   ├── faq_entries.md       # Human-approved FAQs
│   └── faq_drafts.md        # Generated drafts (pending)
├── config.py                # Updated with FAQ configs
├── ingestion.py            # CLI ingestion (keep for now)
├── query.py                # CLI query (keep for now)
├── pipeline/
│   └── index_builder.py    # Refactored
├── agent/
│   └── qa.py               # Core QA logic
├── scripts/
│   └── run_api.py          # API runner
└── requirements.txt        # + fastapi, uvicorn, aiosqlite
```

---

## Data Flow

### Query Flow (Cache-First)

```
Incoming Query
      │
      ▼
┌─────────────────┐
│  Exact Match    │──Yes──▶ Return cached answer
│    in cache     │
└────────┬────────┘
         │ No
         ▼
┌─────────────────┐
│  Semantic Match │──Yes──▶ Return cached answer + update hit count
│  (cosim > 0.9)  │
└────────┬────────┘
         │ No
         ▼
    Process via LLM
    (normal flow)
         │
         ▼
    Log query for FAQ
```

### FAQ Generation Flow (Bi-Weekly / Manual)

```
1. Scheduler triggers (bi-weekly)
       │
       ▼
2. QueryLogger aggregates queries
       │
       ▼
3. FAQGenerator clusters similar queries (cosim > 0.9, count >= 3)
       │
       ▼
4. Generate FAQ drafts from indexed documents
       │
       ▼
5. Write to data/faq_drafts.md (NOT auto-ingested)
       │
       ▼
6. Human reviews/edits in data/faq_entries.md
       │
       ▼
7. Admin calls POST /faq/approve → re-ingest
```

---

## Notes

- Documents located in `./.input` directory
- FAQ files are Markdown for human editability
- Service can be embedded in another agentic AI as subagent
- `RAGService` can be used in-process (no HTTP overhead)
