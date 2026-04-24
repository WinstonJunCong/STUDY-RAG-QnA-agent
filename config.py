# config.py — tweak these to change models / behaviour
import os

# ---------------- Google GenAI ----------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = "gemini-3.1-flash-lite-preview"

# ---------------- Embedding ----------------
EMBED_MODEL = "gemini-embedding-001"

# ---------------- Retrieval ----------------
TOP_K = 6              # chunks returned by retriever
MMR_LAMBDA = 0.7      # 0=max diversity, 1=max relevance

# ---------------- Hybrid Retrieval ----------------
BM25_TOP_K = 8        # BM25 candidates (higher to capture more before fusion)
USE_BM25 = True       # Enable BM25 alongside vector search

# ---------------- Storage ----------------
CHROMA_PATH = "./data/chroma_db"
CHROMA_COLLECTION = "qna_docs"

# ---------------- Memory (Vector-backed) ----------------
MEMORY_TOKEN_LIMIT = 2000      # tokens for recent messages in context
MEMORY_TOP_K = 3               # vector search results for memory retrieval

# ---------------- Unstructured.io chunking params ----------------
CHUNK_MAX_CHARS = 2000      # hard ceiling per chunk
CHUNK_SOFT_LIMIT = 1000    # preferred split point
CHUNK_MIN_CHARS = 350      # merge sections smaller than this

# ---------------- Debugging ----------------
DEBUG_LLM = True
DEBUG_TIMING = True
