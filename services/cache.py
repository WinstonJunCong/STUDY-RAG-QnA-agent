# cache.py
# Query cache with exact + semantic matching

import json
import os
from typing import Optional
from pathlib import Path
import numpy as np

import config


class QueryCache:
    """
    Cache for query answers.
    - Exact match: O(1) lookup
    - Semantic match: cosine similarity > threshold
    """

    def __init__(self, cache_file: str = "./data/query_cache.json"):
        self.cache_file = cache_file
        self._cache: dict = {}
        self._embeddings: dict = {}
        self._load()

    def _load(self):
        """Load cache from disk."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._cache = data.get("queries", {})
                self._embeddings = data.get("embeddings", {})

    def _save(self):
        """Save cache to disk."""
        os.makedirs(os.path.dirname(self.cache_file) or ".", exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump({
                "queries": self._cache,
                "embeddings": self._embeddings
            }, f, ensure_ascii=False)

    def get(self, query: str, embedding: Optional[np.ndarray] = None) -> Optional[dict]:
        """
        Get cached answer for query.
        Checks exact match first, then semantic match.
        
        Returns dict with answer + source if found, None otherwise.
        """
        query_lower = query.lower().strip()

        # Exact match
        if query_lower in self._cache:
            entry = self._cache[query_lower]
            entry["hit_type"] = "exact"
            entry["hit_count"] = entry.get("hit_count", 0) + 1
            self._save()
            return entry

        # Semantic match (if embedding provided)
        if embedding is not None and self._embeddings:
            best_match = None
            best_score = 0

            for cached_query, cached_emb in self._embeddings.items():
                if isinstance(cached_emb, list):
                    cached_emb = np.array(cached_emb)

                # Cosine similarity
                similarity = np.dot(embedding, cached_emb) / (
                    np.linalg.norm(embedding) * np.linalg.norm(cached_emb) + 1e-8
                )

                if similarity >= config.SIMILARITY_THRESHOLD and similarity > best_score:
                    best_score = similarity
                    best_match = cached_query

            if best_match:
                entry = self._cache[best_match].copy()
                entry["hit_type"] = "semantic"
                entry["similarity"] = float(best_score)
                entry["hit_count"] = entry.get("hit_count", 0) + 1
                self._save()
                return entry

        return None

    def set(self, query: str, answer: str, sources: list, embedding: Optional[np.ndarray] = None):
        """Cache a query-answer pair."""
        query_lower = query.lower().strip()

        self._cache[query_lower] = {
            "answer": answer,
            "sources": sources
        }

        if embedding is not None:
            self._embeddings[query_lower] = embedding.tolist() if hasattr(embedding, 'tolist') else embedding

        self._save()

    def clear(self):
        """Clear all cached entries."""
        self._cache = {}
        self._embeddings = {}
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "total_entries": len(self._cache),
            "exact_matches": len(self._cache),
            "semantic_matches": len(self._embeddings)
        }


def get_query_cache() -> QueryCache:
    """Get singleton query cache."""
    return QueryCache()
