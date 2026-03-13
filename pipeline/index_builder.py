# pipeline/index_builder.py
# Takes raw Documents, chunks them, embeds with a free local model,
# and stores in ChromaDB on disk.

import chromadb
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

import config


def configure_settings():
    """
    Set global LlamaIndex settings to use free local models only.
    Call this once before building or querying the index.
    """
    Settings.embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL)
    Settings.llm = Ollama(model=config.OLLAMA_MODEL, base_url=config.OLLAMA_BASE_URL)
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
