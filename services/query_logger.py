# query_logger.py
# Query logger using DB abstraction (SQLite or PostgreSQL)

from typing import Optional
from services.database import get_query_store


class QueryLogger:
    """
    Logs queries using configured backend (SQLite or PostgreSQL).
    """

    def __init__(self):
        self._store = get_query_store()

    def log_query(
        self,
        query_text: str,
        answer: Optional[str] = None,
        hit_cache: bool = False,
        embedding: Optional[bytes] = None
    ):
        """Log a query."""
        self._store.log_query(query_text, answer, hit_cache, embedding)

    def get_recent_queries(self, hours: int = 336) -> list:
        """Get queries from the last N hours."""
        return self._store.get_recent_queries(hours)

    def get_all_queries(self) -> list:
        """Get all logged queries."""
        return self._store.get_all_queries()

    def get_query_count(self) -> int:
        """Get total query count."""
        return self._store.get_query_count()

    def clear(self):
        """Clear all logged queries."""
        self._store.clear()


def get_query_logger() -> QueryLogger:
    """Get singleton query logger."""
    return QueryLogger()
