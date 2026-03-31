# config.py — tweak these to change models / behaviour

# ---------------- Embedding ----------------
EMBED_MODEL = "BAAI/bge-base-en-v1.5"

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
CHUNK_MAX_CHARS = 2000      # hard ceiling per chunk
CHUNK_SOFT_LIMIT = 1000    # preferred split point
CHUNK_MIN_CHARS = 350      # merge sections smaller than this

# ---------------- Debugging ----------------
DEBUG_LLM = True
DEBUG_TIMING = True
