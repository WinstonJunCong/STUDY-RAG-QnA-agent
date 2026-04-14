# rag_service.py
# Core RAG service - wraps query/ingestion logic for API usage

import time
import json
from pathlib import Path
from typing import Optional

from llama_index.core import VectorStoreIndex

import config
from pipeline.index_builder import (
    configure_settings,
    build_index as build_index_from_docs,
    load_index as load_index_from_db,
    get_vector_store,
    delete_index as clear_chroma_index,
)


class RAGService:
    """
    Core RAG service for querying and ingestion.
    Can be used in-process or via API.
    """

    _instance = None
    _index: Optional[VectorStoreIndex] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._index = None
        self._index_stats = {"chunk_count": 0, "last_updated": None}

    @property
    def index_loaded(self) -> bool:
        return self._index is not None

    @property
    def index_stats(self) -> dict:
        return self._index_stats

    def load_index(self) -> VectorStoreIndex:
        """Load existing index from ChromaDB."""
        if self._index is None:
            configure_settings()
            self._index = load_index_from_db()
            self._update_stats()
        return self._index

    def _update_stats(self):
        """Update index statistics."""
        if self._index is None:
            self._index_stats = {"chunk_count": 0, "last_updated": None}
            return

        try:
            chroma_client = get_vector_store()
            collection = chroma_client._collection
            count = collection.count()
            self._index_stats = {
                "chunk_count": count,
                "last_updated": self._get_timestamp()
            }
        except Exception:
            self._index_stats = {"chunk_count": 0, "last_updated": None}

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()

    def ingest(self, text_folders: list[str] = None, force_rebuild: bool = False) -> dict:
        """
        Rebuild the index from documents.

        Args:
            text_folders: List of folders to ingest (defaults to config.TEXT_FOLDERS)
            force_rebuild: If True, clear existing index first

        Returns:
            dict with status, chunk_count, timing_ms
        """
        start_time = time.perf_counter()

        if text_folders is None:
            text_folders = config.TEXT_FOLDERS

        from ingest.text_loader import load_text_files
        all_docs = []

        for folder in text_folders:
            docs = load_text_files(folder)
            all_docs.extend(docs)

        if not all_docs:
            return {
                "status": "error",
                "message": "No documents found",
                "chunks": 0,
                "timing_ms": 0
            }

        if force_rebuild:
            self.delete_index()

        configure_settings()
        self._index = build_index_from_docs(all_docs)
        self._update_stats()

        elapsed = (time.perf_counter() - start_time) * 1000

        return {
            "status": "ok",
            "chunks": self._index_stats["chunk_count"],
            "documents": len(all_docs),
            "timing_ms": int(elapsed)
        }

    def query(self, question: str, top_k: int = None) -> dict:
        """
        Query the RAG system.

        Args:
            question: The question to ask
            top_k: Number of chunks to retrieve (defaults to config.TOP_K)

        Returns:
            dict with answer, sources, timing_ms
        """
        from agent.qa import ask

        if top_k is None:
            top_k = config.TOP_K

        start_time = time.perf_counter()

        index = self.load_index()

        result = ask(question, index)

        elapsed = (time.perf_counter() - start_time) * 1000

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "timing_ms": int(elapsed)
        }

    def delete_index(self) -> dict:
        """Clear the vector index."""
        clear_chroma_index()
        self._index = None
        self._index_stats = {"chunk_count": 0, "last_updated": None}
        return {"status": "deleted"}

    def get_status(self) -> dict:
        """Get service status."""
        return {
            "index_loaded": self.index_loaded,
            "index_stats": self._index_stats
        }


def get_rag_service() -> RAGService:
    """Get singleton RAG service instance."""
    return RAGService()
