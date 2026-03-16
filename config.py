# config.py — tweak these to change models / behaviour

# ---------------- Embedding ----------------
# Free, runs locally. Good balance of speed vs quality.
# Alternatives:
#   "BAAI/bge-large-en-v1.5"   → better quality, slower
#   "all-MiniLM-L6-v2"         → fastest, slightly lower quality
EMBED_MODEL = "BAAI/bge-small-en-v1.5"

# ---------------- LLM (via Ollama) ----------------
# Run `ollama pull llama3.2` before using.
# Alternatives (all free via Ollama):
#   "mistral"      → fast, great for Q&A
#   "llama3.2"     → best overall quality
#   "phi3"         → lightweight, good for low-RAM machines
OLLAMA_MODEL = "llama3.2" #"phi3:mini"
OLLAMA_BASE_URL = "http://localhost:11434"

# ---------------- Chunking ----------------
CHUNK_SIZE = 512        # tokens per chunk
CHUNK_OVERLAP = 100      # overlap between chunks (helps context continuity)

# ---------------- Retrieval ----------------
TOP_K = 5               # how many chunks to retrieve per question

# ---------------- Storage ----------------
CHROMA_PATH = "./chroma_db"         # where ChromaDB persists on disk
CHROMA_COLLECTION = "qna_docs"
