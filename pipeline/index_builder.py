# pipeline/index_builder.py
# Uses Unstructured.io for semantic document parsing.
# Automatically handles markdown, tables, lists, and preserves heading hierarchy.

# Load .env file at the very top - BEFORE any other imports
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Set cache locations from .env - ensures models load from D: drive
HF_HOME = os.getenv("HF_HOME", "D:\\huggingface_cache")
os.environ["HF_HOME"] = HF_HOME
os.environ["TRANSFORMERS_CACHE"] = os.getenv("TRANSFORMERS_CACHE", f"{HF_HOME}\\transformers")

# Force GPU usage for embedding model
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import chromadb
import json
from llama_index.core import VectorStoreIndex, StorageContext, Settings, Document
from llama_index.core.schema import TextNode
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from unstructured.partition.md import partition_md
from unstructured.partition.text import partition_text
from unstructured.chunking.title import chunk_by_title
from pathlib import Path

import config


class OctenEmbedding(HuggingFaceEmbedding):
    """
    Custom wrapper for Octen embedding model.
    Adds "- " prefix to documents to avoid Qwen3-Embedding upstream issue.
    See: https://huggingface.co/Qwen/Qwen3-Embedding-8B/discussions/21
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _embed(self, inputs: list[str], prompt_name: str | None = None) -> list[list[float]]:
        prefixed_inputs = ["- " + text for text in inputs]
        return super()._embed(prefixed_inputs, prompt_name)


def configure_settings():
    """Set global LlamaIndex settings."""
    if config.USE_EXTERNAL_EMBED == "true":
        from llama_index.embeddings.openai import OpenAIEmbedding
        
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",  # Placeholder - works with any OpenAI-compatible server
            api_key="dummy",
            api_base=config.EMBED_SERVER_URL,
        )
        print(f"[settings] Embed: {config.EMBED_SERVER_URL} (external)")
    else:
        Settings.embed_model = OctenEmbedding(model_name=config.EMBED_MODEL, device="cuda")
        print(f"[settings] Embed: {config.EMBED_MODEL} (local)")
    
    print(f"[settings] LLM: {config.LLM_SERVER_URL} ({config.LLM_MODEL}) - uses direct OpenAI")


def get_vector_store():
    """Returns a ChromaDB-backed vector store (persisted to disk)."""
    db = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    collection = db.get_or_create_collection(config.CHROMA_COLLECTION)
    return ChromaVectorStore(chroma_collection=collection)


def partition_document(filepath: str):
    """
    Partition a document into elements using Unstructured.
    Automatically handles .md, .txt (transcripts), .pdf, .html
    """
    path = Path(filepath)
    ext = path.suffix.lower()

    if ext == ".md":
        return partition_md(filename=filepath)
    elif ext in (".txt", ".vtt", ".srt"):
        return partition_text(filename=filepath)
    else:
        from unstructured.partition.auto import partition
        return partition(filename=filepath)


def elements_to_nodes(chunks, source_file: str) -> list[TextNode]:
    """
    Convert Unstructured chunks into LlamaIndex TextNodes.
    Preserves all metadata: heading hierarchy, element type, source.
    """
    nodes = []
    for chunk in chunks:
        text = chunk.text.strip()
        if not text:
            continue

        meta = {
            "filename": Path(source_file).name,
            "source": source_file,
            "element_type": type(chunk).__name__,
        }

        if hasattr(chunk, "metadata"):
            um = chunk.metadata
            if hasattr(um, "page_number") and um.page_number:
                meta["page"] = um.page_number
            if hasattr(um, "parent_id") and um.parent_id:
                meta["parent_id"] = str(um.parent_id)
            if hasattr(um, "filename") and um.filename:
                meta["filename"] = Path(um.filename).name

        nodes.append(TextNode(text=text, metadata=meta))

    return nodes


def build_index(documents: list[Document]) -> VectorStoreIndex:
    """
    Full ingestion pipeline:
    1. Partition with Unstructured (structure-aware)
    2. Chunk by title sections (keeps Q&A pairs together)
    3. Convert to LlamaIndex nodes
    4. Embed and store in ChromaDB
    """
    configure_settings()

    chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    try:
        chroma_client.delete_collection(config.CHROMA_COLLECTION)
        print(f"[index_builder] Cleared existing ChromaDB collection")
    except Exception:
        pass

    all_nodes = []
    for doc in documents:
        filepath = doc.metadata.get("file_path", "")
        if not filepath or not Path(filepath).exists():
            continue

        print(f"   Parsing: {Path(filepath).name}")

        elements = partition_document(filepath)

        chunks = chunk_by_title(
            elements,
            max_characters=config.CHUNK_MAX_CHARS,
            new_after_n_chars=config.CHUNK_SOFT_LIMIT,
            combine_text_under_n_chars=config.CHUNK_MIN_CHARS,
            multipage_sections=True,
        )

        nodes = elements_to_nodes(chunks, filepath)
        all_nodes.extend(nodes)
        print(f"      -> {len(nodes)} chunks")

    print(f"[index_builder] Total chunks: {len(all_nodes)}")

    # Save nodes to JSON for BM25 retriever
    bm25_path = "./data/bm25_nodes.json"
    nodes_data = [
        {
            "id": node.node_id,
            "text": node.text,
            "metadata": node.metadata
        }
        for node in all_nodes
    ]
    with open(bm25_path, "w", encoding="utf-8") as f:
        json.dump(nodes_data, f, ensure_ascii=False)
    print(f"[index_builder] Saved {len(nodes_data)} nodes to {bm25_path} for BM25")

    vector_store = get_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print(f"[index_builder] Embedding {len(all_nodes)} chunks into ChromaDB...")
    index = VectorStoreIndex(
        all_nodes,
        storage_context=storage_context,
        show_progress=True,
    )

    print(f"[index_builder] Index built — {len(all_nodes)} chunks in ChromaDB")
    return index


def load_index() -> VectorStoreIndex:
    """Load existing index from ChromaDB."""
    configure_settings()
    vector_store = get_vector_store()
    index = VectorStoreIndex.from_vector_store(vector_store)
    print("[index_builder] Index loaded from ChromaDB")
    return index


def delete_index():
    """Delete the ChromaDB collection."""
    chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    try:
        chroma_client.delete_collection(config.CHROMA_COLLECTION)
        print("[index_builder] Deleted ChromaDB collection")
    except Exception as e:
        print(f"[index_builder] No collection to delete: {e}")


def add_document_to_index(filepath: str) -> dict:
    """
    Add a single document to the existing index.
    Used for file upload ingestion.
    """
    path = Path(filepath)
    if not path.exists():
        return {"status": "error", "message": f"File not found: {filepath}"}
    
    configure_settings()
    
    print(f"   Parsing: {path.name}")
    elements = partition_document(filepath)
    
    chunks = chunk_by_title(
        elements,
        max_characters=config.CHUNK_MAX_CHARS,
        new_after_n_chars=config.CHUNK_SOFT_LIMIT,
        combine_text_under_n_chars=config.CHUNK_MIN_CHARS,
        multipage_sections=True,
    )
    
    nodes = elements_to_nodes(chunks, filepath)
    print(f"      -> {len(nodes)} chunks")
    
    # Add to existing index
    from services.rag_service import get_rag_service
    rag = get_rag_service()
    index = rag.load_index()
    
    for node in nodes:
        index.insert(node)
    
    # Update BM25
    bm25_path = "./data/bm25_nodes.json"
    if Path(bm25_path).exists():
        with open(bm25_path, "r", encoding="utf-8") as f:
            nodes_data = json.load(f)
    else:
        nodes_data = []
    
    nodes_data.extend([
        {
            "id": node.node_id,
            "text": node.text,
            "metadata": node.metadata
        }
        for node in nodes
    ])
    
    with open(bm25_path, "w", encoding="utf-8") as f:
        json.dump(nodes_data, f, ensure_ascii=False)
    
    return {
        "status": "ok",
        "chunks": len(nodes),
        "file": path.name
    }
