# config.py — tweak these to change models / behaviour

# ---------------- Embedding ----------------
# Free, runs locally. Good balance of speed vs quality.
# Alternatives:
#   "BAAI/bge-large-en-v1.5"   → better quality, slower
#   "all-MiniLM-L6-v2"         → fastest, slightly lower quality
EMBED_MODEL = "BAAI/bge-base-en-v1.5"

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
CHUNK_OVERLAP = 128    # overlap between chunks (helps context continuity)

# ---------------- Retrieval ----------------
TOP_K = 8               # how many chunks to retrieve per question

# ---------------- Storage ----------------
CHROMA_PATH = "./chroma_db"         # where ChromaDB persists on disk
CHROMA_COLLECTION = "qna_docs"

# ---------------- Debugging ----------------
DEBUG_LLM = False      # Set to True to print exact prompts and raw LLM responses to the console

# ---------------- Advanced Retrieval ----------------
USE_HYDE = True                            # HyDE: embed a hypothetical answer instead of raw question
USE_RERANKER = True                        # Reranker: second-pass re-scoring of retrieved chunks
RERANKER_MODEL = "BAAI/bge-reranker-base" # cross-encoder model for reranking
TOP_N = 5                                  # chunks to keep after reranking (from TOP_K raw candidates)
