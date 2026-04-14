# query_logger.py
# SQLite-based query logger with embeddings for FAQ generation

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional
from pathlib import Path

import config


class QueryLogger:
    """
    Logs queries to SQLite for FAQ generation.
    Stores: query text, timestamp, embedding (for semantic clustering)
    """

    def __init__(self, db_path: str = "./data/query_log.db"):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """Create tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                answer TEXT,
                hit_cache BOOLEAN DEFAULT 0,
                embedding BLOB
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON queries(timestamp)
        """)
        conn.commit()
        conn.close()

    def log_query(
        self,
        query_text: str,
        answer: Optional[str] = None,
        hit_cache: bool = False,
        embedding: Optional[bytes] = None
    ):
        """Log a query."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO queries (query_text, timestamp, answer, hit_cache, embedding) VALUES (?, ?, ?, ?, ?)",
            (query_text, datetime.now().isoformat(), answer, hit_cache, embedding)
        )
        conn.commit()
        conn.close()

    def get_recent_queries(self, hours: int = 336) -> list:
        """
        Get queries from the last N hours.
        Default: 336 hours = 2 weeks (bi-weekly FAQ generation)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, query_text, timestamp, answer, hit_cache
            FROM queries
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
            """,
            (hours,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "query_text": row[1],
                "timestamp": row[2],
                "answer": row[3],
                "hit_cache": bool(row[4])
            }
            for row in rows
        ]

    def get_all_queries(self) -> list:
        """Get all logged queries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, query_text, timestamp, answer, hit_cache FROM queries ORDER BY timestamp DESC"
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "query_text": row[1],
                "timestamp": row[2],
                "answer": row[3],
                "hit_cache": bool(row[4])
            }
            for row in rows
        ]

    def get_query_count(self) -> int:
        """Get total query count."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM queries")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def clear(self):
        """Clear all logged queries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM queries")
        conn.commit()
        conn.close()


def get_query_logger() -> QueryLogger:
    """Get singleton query logger."""
    return QueryLogger()
