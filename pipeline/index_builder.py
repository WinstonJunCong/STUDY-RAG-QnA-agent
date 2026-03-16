# pipeline/index_builder.py
# Takes raw Documents, chunks them, embeds with a free local model,
# and stores in ChromaDB on disk.

import os
import psutil
import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

import config


def print_diagnostics():
    """Print system RAM usage, GPU info, and which device models will use."""
    print("\n" + "="*50)
    print("🔍 DIAGNOSTICS")
    print("="*50)

    # --- System RAM ---
    ram = psutil.virtual_memory()
    print(f"💾 System RAM : {ram.used / 1e9:.1f} GB used / {ram.total / 1e9:.1f} GB total ({ram.percent}%)")

    # --- GPU check via nvidia-smi ---
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                name, mem_used, mem_total, util = [x.strip() for x in line.split(",")]
                print(f"🎮 GPU        : {name}")
                print(f"   VRAM      : {mem_used} MB used / {mem_total} MB total")
                print(f"   Utilization: {util}%")
        else:
            print("🎮 GPU        : nvidia-smi not available or no NVIDIA GPU found")
    except Exception:
        print("🎮 GPU        : Could not query GPU (nvidia-smi not found)")

    # --- Ollama model info ---
    try:
        import subprocess
        result = subprocess.run(["ollama", "ps"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            print(f"🤖 Ollama running models:\n{result.stdout.strip()}")
        else:
            print(f"🤖 Ollama model : {config.OLLAMA_MODEL} (not yet loaded into memory)")
    except Exception:
        print(f"🤖 Ollama model : {config.OLLAMA_MODEL} (could not query ollama ps)")

    # --- Embedding device ---
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🧮 Embed device : {device.upper()} ({'GPU' if device == 'cuda' else 'CPU — no CUDA available'})")
    except ImportError:
        print("🧮 Embed device : torch not found, defaulting to CPU")

    print("="*50 + "\n")


def configure_settings():
    """
    Set global LlamaIndex settings to use free local models only.
    Call this once before building or querying the index.
    """
    if config.DEBUG_LLM:
        print_diagnostics()  # 👈 debug info printed here before models load

    Settings.embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL)
    # print(f"[debug] Loading Ollama with model='{config.OLLAMA_MODEL}'")
    Settings.llm = Ollama(
        model=config.OLLAMA_MODEL, 
        base_url=config.OLLAMA_BASE_URL,
        request_timeout=120.0,
        )
    # Settings.llm = Ollama(
    # model=config.OLLAMA_MODEL,           # hardcoded, not from config, just to test
    # base_url=config.OLLAMA_BASE_URL,
    # request_timeout=600.0,
    # context_window=128000,    # 👈 hard cap, phi3:mini supports 4096 max
    # num_output=2048,         # 👈 cap the response length too
    # )

    # Inspect the actual object
    # print(f"[debug] Settings.llm object model = '{Settings.llm.model}'")
    # print(f"[debug] Settings.llm type = {type(Settings.llm)}")
    # print(f"[debug] Settings.llm full config = {Settings.llm.__dict__}")
    Settings.chunk_size = config.CHUNK_SIZE
    Settings.chunk_overlap = config.CHUNK_OVERLAP
    print(f"[settings] Embed: {config.EMBED_MODEL} | LLM: {config.OLLAMA_MODEL}")


def get_vector_store():
    """Returns a ChromaDB-backed vector store (persisted to disk)."""
    db = chromadb.PersistentClient(path=config.CHROMA_PATH)
    collection = db.get_or_create_collection(config.CHROMA_COLLECTION)
    return ChromaVectorStore(chroma_collection=collection)


def build_index(documents: list[Document]) -> VectorStoreIndex:
    """
    Chunk, embed, and store documents. Returns a queryable index.
    Safe to call multiple times — new docs are added, existing ones aren't duplicated.
    """
    configure_settings()
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    splitter = SentenceSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[splitter],
        show_progress=True,
    )

    print(f"[index_builder] Indexed {len(documents)} documents into ChromaDB at {config.CHROMA_PATH}")
    return index


def load_index() -> VectorStoreIndex:
    """
    Load an existing index from ChromaDB (no re-embedding needed).
    Call this in your Q&A loop instead of rebuild_index every time.
    """
    configure_settings()
    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)