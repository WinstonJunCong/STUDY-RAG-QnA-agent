# pipeline/index_builder.py
# Uses Unstructured.io for semantic document parsing.
# Automatically handles markdown, tables, lists, and preserves heading hierarchy.

import chromadb
import json
from llama_index.core import VectorStoreIndex, StorageContext, Settings, Document
from llama_index.core.schema import TextNode
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from unstructured.partition.md import partition_md
from unstructured.partition.text import partition_text
from unstructured.chunking.title import chunk_by_title
from pathlib import Path

import config


def configure_settings():
    """Set global LlamaIndex settings."""
    Settings.embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL)
    Settings.llm = Ollama(
        model=config.OLLAMA_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        request_timeout=120.0,
    )
    print(f"[settings] Embed: {config.EMBED_MODEL} | LLM: {config.OLLAMA_MODEL}")


def get_vector_store():
    """Returns a ChromaDB-backed vector store (persisted to disk)."""
    db = chromadb.PersistentClient(path=config.CHROMA_PATH)
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

    chroma_client = chromadb.PersistentClient(path=config.CHROMA_PATH)
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
