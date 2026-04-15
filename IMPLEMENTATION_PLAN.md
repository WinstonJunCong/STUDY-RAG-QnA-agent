# Implementation Plan: CLI to API Transformation

## Overview

Transform the current CLI-based RAG system into a FastAPI microservice for a 3D animation studio knowledge base.

## Domain

Documents about:
- DCC tools (Maya, Blender, 3ds Max, Motion Builder, Unreal)
- AI tools and addons
- Training materials
- Studio workflow documentation

---

## Phased Implementation

### Phase 1: Core API (COMPLETED)

**Status:** ✅ Complete

- FastAPI server with all CRUD endpoints
- RAGService singleton
- Query cache (exact match)
- SQLite query logger
- FAQ endpoints with human review workflow

---

### Phase 2: External DB Support + Async Ingestion (IN PROGRESS)

**Goal:** PostgreSQL support, async file upload ingestion

**Status:** 🔄 In Progress

#### Configuration

Environment Variables (`.env`):

```bash
# Database - PostgreSQL (query log)
DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=studio_kb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# ChromaDB (persistent storage)
CHROMA_PERSIST_DIR=./data/chroma_db

# Ollama (LLM)
OLLAMA_BASE_URL=http://localhost:11434
```

#### Database Abstraction

```python
# services/database/query_store.py
class QueryStore(Protocol):
    def log_query(...)
    def get_recent_queries(...)
    def get_query_count(...)
    def clear(...)
```

**Auto-detect:** If `DB_TYPE=postgresql` and env vars present → use PostgreSQL, otherwise fallback to SQLite.

#### Async Ingestion with Job Queue

**API Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ingest` | POST | Start async ingestion (returns job_id) |
| `/ingest/upload` | POST | Upload file + start ingestion |
| `/jobs/{job_id}` | GET | Get job status |
| `/jobs` | GET | List all jobs |

**Job Model:**
```python
class IngestionJob:
    job_id: str
    status: "pending" | "processing" | "completed" | "failed" | "cancelled"
    source: str  # "folder", "upload", "url", "text"
    file_path: str | None
    progress: int  # 0-100
    result: dict | None
    error: str | None
    created_at: datetime
    completed_at: datetime | None
```

#### File Upload

```python
# POST /ingest/upload
- Accept: multipart/form-data
- Save to: ./data/uploads/{job_id}_{filename}
- Queue ingestion job
- Return job_id immediately
```

**Supported:** `.txt`, `.md`, `.pdf`, `.docx`, `.html`

**Cleanup:** Files deleted after processing completes.

---

### Phase 3: FAQ Auto-Enhancement (PENDING)

**Goal:** Bi-weekly FAQ generation with human review workflow

**Deliverables:**
- Query clustering (semantic similarity > 0.9, count >= 3)
- FAQ draft generation from indexed documents
- Human review workflow (markdown files)
- Bi-weekly scheduler

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
│       ├── query.py         # /query
│       ├── ingest.py        # /ingest (async)
│       ├── jobs.py          # /jobs
│       ├── index.py         # /index/*
│       ├── faq.py           # /faq/*
│       └── cache.py         # /cache/*
├── services/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── query_store.py
│   │   │   ├── sqlite_store.py
│   │   │   └── postgres_store.py
│   │   └── vector_store.py
│   │       └── chroma_store.py
│   ├── rag_service.py       # Core RAG service
│   ├── query_logger.py      # Uses DB abstraction
│   ├── cache.py             # Query cache
│   ├── job_queue.py         # Async job processing
│   └── scheduler.py         # Bi-weekly scheduler
├── data/
│   ├── uploads/             # Temporary upload storage
│   ├── faq_entries.md       # Human-approved FAQs
│   └── faq_drafts.md        # Generated drafts
├── config.py                # Environment-based config
├── ingestion.py             # CLI ingestion
├── query.py                 # CLI query
├── pipeline/
│   └── index_builder.py    # Refactored
├── agent/
│   └── qa.py                # Core QA logic
├── scripts/
│   └── run_api.py           # API runner
└── requirements.txt
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
    Process via LLM
    (normal flow)
         │
         ▼
    Log query (PostgreSQL/SQLite)
```

### Async Ingestion Flow

```
POST /ingest/upload (file)
      │
      ▼
Save file to ./data/uploads/
      │
      ▼
Create job (status: pending)
      │
      ▼
Return job_id immediately
      │
      ▼
Background worker picks up job
      │
      ▼
Process document → Embed → Store in ChromaDB
      │
      ▼
Update job status (completed/failed)
      │
      ▼
Cleanup temp file
```

---

## Notes

- Documents located in `./.input` directory
- FAQ files are Markdown for human editability
- Service can be embedded in another agentic AI as subagent
- PostgreSQL used for query logging, ChromaDB for vectors
- Job queue in-memory (can be extended to Redis later)
