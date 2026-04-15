# services/database/base.py
# Abstract base classes for database backends

from typing import Protocol, Optional
from datetime import datetime


class QueryStore(Protocol):
    """Protocol for query storage backends."""
    
    def log_query(
        self,
        query_text: str,
        answer: Optional[str] = None,
        hit_cache: bool = False,
        embedding: Optional[bytes] = None
    ) -> None:
        """Log a query."""
        ...
    
    def get_recent_queries(self, hours: int = 336) -> list[dict]:
        """Get queries from the last N hours."""
        ...
    
    def get_all_queries(self) -> list[dict]:
        """Get all logged queries."""
        ...
    
    def get_query_count(self) -> int:
        """Get total query count."""
        ...
    
    def clear(self) -> None:
        """Clear all logged queries."""
        ...


class VectorStore(Protocol):
    """Protocol for vector storage backends."""
    
    def add_documents(self, nodes: list) -> int:
        """Add documents to the index. Returns chunk count."""
        ...
    
    def query(self, query_embedding: list[float], top_k: int) -> list:
        """Query the index."""
        ...
    
    def delete_all(self) -> None:
        """Clear the index."""
        ...
    
    def get_stats(self) -> dict:
        """Get index statistics."""
        ...
