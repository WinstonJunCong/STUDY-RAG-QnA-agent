# config.py — tweak these to change models / behaviour

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------- Embedding ----------------
EMBED_MODEL = os.getenv("EMBED_MODEL", "D:\\huggingface_models\\Octen-8B")

# ---------------- LLM (via Ollama) ----------------
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ---------------- Database Configuration ----------------
# DB_TYPE: "sqlite" or "postgresql"
DB_TYPE = os.getenv("DB_TYPE", "sqlite")

# PostgreSQL (query log)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "studio_kb")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# ChromaDB (vector store)
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
CHROMA_COLLECTION = "qna_docs"

# Backward compatibility alias
CHROMA_PATH = CHROMA_PERSIST_DIR

# ---------------- Retrieval ----------------
TOP_K = 6              # chunks returned by retriever
MMR_LAMBDA = 0.7      # 0=max diversity, 1=max relevance

# ---------------- Hybrid Retrieval ----------------
BM25_TOP_K = 8        # BM25 candidates (higher to capture more before fusion)
USE_BM25 = True       # Enable BM25 alongside vector search

# ---------------- Unstructured.io chunking params ----------------
CHUNK_MAX_CHARS = 8000      # hard ceiling per chunk (Octen supports 32K context)
CHUNK_SOFT_LIMIT = 4000    # preferred split point
CHUNK_MIN_CHARS = 700      # merge sections smaller than this

# ---------------- Ingestion ----------------
TEXT_FOLDERS = [
    "./.input",
]

# File upload settings
UPLOAD_DIR = "./data/uploads"
MAX_UPLOAD_SIZE_MB = 50

# ---------------- FAQ Auto-Enhancement ----------------
FAQ_ENTRIES_FILE = "./data/faq_entries.md"
FAQ_DRAFTS_FILE = "./data/faq_drafts.md"
SIMILARITY_THRESHOLD = 0.9      # Query deduplication threshold
MIN_QUERY_COUNT = 3             # Min queries to trigger FAQ generation
FAQ_SCHEDULE = "biweekly"        # "biweekly" or "manual"

# ---------------- Debugging ----------------
DEBUG_LLM = False
DEBUG_TIMING = False
