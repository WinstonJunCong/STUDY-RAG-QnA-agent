# config.py — tweak these to change models / behaviour

# ---------------- Embedding ----------------
EMBED_MODEL = "D:\\huggingface_models\\Octen-8B"

# ---------------- LLM (via Ollama) ----------------
OLLAMA_MODEL = "mistral"
OLLAMA_BASE_URL = "http://localhost:11434"

# ---------------- Retrieval ----------------
TOP_K = 6              # chunks returned by retriever
MMR_LAMBDA = 0.7      # 0=max diversity, 1=max relevance

# ---------------- Hybrid Retrieval ----------------
BM25_TOP_K = 8        # BM25 candidates (higher to capture more before fusion)
USE_BM25 = True       # Enable BM25 alongside vector search

# ---------------- Storage ----------------
CHROMA_PATH = "./data/chroma_db"
CHROMA_COLLECTION = "qna_docs"

# ---------------- Unstructured.io chunking params ----------------
CHUNK_MAX_CHARS = 8000      # hard ceiling per chunk (Octen supports 32K context)
CHUNK_SOFT_LIMIT = 4000    # preferred split point
CHUNK_MIN_CHARS = 700      # merge sections smaller than this

# ---------------- Ingestion ----------------
TEXT_FOLDERS = [
    "./.input",
]

# ---------------- FAQ Auto-Enhancement ----------------
FAQ_ENTRIES_FILE = "./data/faq_entries.md"
FAQ_DRAFTS_FILE = "./data/faq_drafts.md"
SIMILARITY_THRESHOLD = 0.9      # Query deduplication threshold
MIN_QUERY_COUNT = 3             # Min queries to trigger FAQ generation
FAQ_SCHEDULE = "biweekly"        # "biweekly" or "manual"

# ---------------- Debugging ----------------
DEBUG_LLM = False
DEBUG_TIMING = False
