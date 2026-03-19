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
OLLAMA_MODEL = "mistral" #"mistral-nemo" #"llama3.2" #"phi3:mini"
OLLAMA_BASE_URL = "http://localhost:11434"

# ---------------- Chunking ----------------
CHUNK_SIZE = 512        # tokens per chunk
CHUNK_OVERLAP = 128    # overlap between chunks (helps context continuity)

# ---------------- Retrieval ----------------
TOP_K = 12              # raw candidates per sub-query (more headroom for MMR after merge)

# ---------------- Storage ----------------
CHROMA_PATH = "./chroma_db"         # where ChromaDB persists on disk
CHROMA_COLLECTION = "qna_docs"

# ---------------- Debugging ----------------
DEBUG_LLM = True      # Set to True to print exact prompts and raw LLM responses to the console
DEBUG_TIMING = True   # Set to True to print timing for each pipeline step

# ---------------- Advanced Retrieval ----------------
USE_HYDE       = False                          # Disabled — hallucination risk for niche/technical docs
USE_RERANKER   = False                          # Disabled — slow; cross-encoder not tuned to your domain

# Multi-Query Expansion: rule-based rephrasings, no LLM required
USE_MULTI_QUERY   = True
MULTI_QUERY_COUNT = 3         # number of query variants (including the original)

# MMR post-filter: keeps chunks that are BOTH relevant AND diverse
USE_MMR    = True
MMR_LAMBDA = 0.6              # 0 = pure diversity · 1 = pure relevance (start at 0.6, tune as needed)
TOP_N      = 5                # final chunks kept after MMR (from the merged TOP_K pool)
