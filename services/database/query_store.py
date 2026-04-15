# services/database/query_store.py
# Query store implementations

import sqlite3
import os
from typing import Optional
from datetime import datetime
from abc import ABC, abstractmethod

import config


class BaseQueryStore:
    """Base class for query stores."""
    
    @abstractmethod
    def log_query(
        self,
        query_text: str,
        answer: Optional[str] = None,
        hit_cache: bool = False,
        embedding: Optional[bytes] = None
    ) -> None:
        pass
    
    @abstractmethod
    def get_recent_queries(self, hours: int = 336) -> list[dict]:
        pass
    
    @abstractmethod
    def get_all_queries(self) -> list[dict]:
        pass
    
    @abstractmethod
    def get_query_count(self) -> int:
        pass
    
    @abstractmethod
    def clear(self) -> None:
        pass


class SQLiteQueryStore(BaseQueryStore):
    """SQLite-based query store."""
    
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO queries (query_text, timestamp, answer, hit_cache, embedding) VALUES (?, ?, ?, ?, ?)",
            (query_text, datetime.now().isoformat(), answer, hit_cache, embedding)
        )
        conn.commit()
        conn.close()
    
    def get_recent_queries(self, hours: int = 336) -> list[dict]:
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
    
    def get_all_queries(self) -> list[dict]:
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM queries")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def clear(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM queries")
        conn.commit()
        conn.close()


class PostgreSQLQueryStore(BaseQueryStore):
    """PostgreSQL-based query store."""
    
    def __init__(self):
        import psycopg2
        self._conn = psycopg2.connect(
            host=config.POSTGRES_HOST,
            port=config.POSTGRES_PORT,
            dbname=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )
        self._ensure_db()
    
    def _ensure_db(self):
        cursor = self._conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id SERIAL PRIMARY KEY,
                query_text TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT NOW(),
                answer TEXT,
                hit_cache BOOLEAN DEFAULT FALSE,
                embedding BYTEA
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON queries(timestamp)
        """)
        self._conn.commit()
        cursor.close()
    
    def log_query(
        self,
        query_text: str,
        answer: Optional[str] = None,
        hit_cache: bool = False,
        embedding: Optional[bytes] = None
    ):
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO queries (query_text, timestamp, answer, hit_cache, embedding) VALUES (%s, %s, %s, %s, %s)",
            (query_text, datetime.now(), answer, hit_cache, embedding)
        )
        self._conn.commit()
        cursor.close()
    
    def get_recent_queries(self, hours: int = 336) -> list[dict]:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT id, query_text, timestamp, answer, hit_cache
            FROM queries
            WHERE timestamp >= NOW() - INTERVAL '%s hours'
            ORDER BY timestamp DESC
            """,
            (hours,)
        )
        rows = cursor.fetchall()
        cursor.close()
        return [
            {
                "id": row[0],
                "query_text": row[1],
                "timestamp": row[2].isoformat() if row[2] else None,
                "answer": row[3],
                "hit_cache": bool(row[4])
            }
            for row in rows
        ]
    
    def get_all_queries(self) -> list[dict]:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, query_text, timestamp, answer, hit_cache FROM queries ORDER BY timestamp DESC"
        )
        rows = cursor.fetchall()
        cursor.close()
        return [
            {
                "id": row[0],
                "query_text": row[1],
                "timestamp": row[2].isoformat() if row[2] else None,
                "answer": row[3],
                "hit_cache": bool(row[4])
            }
            for row in rows
        ]
    
    def get_query_count(self) -> int:
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM queries")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    
    def clear(self):
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM queries")
        self._conn.commit()
        cursor.close()
    
    def close(self):
        self._conn.close()


def get_query_store() -> BaseQueryStore:
    """Get query store based on configuration."""
    if config.DB_TYPE == "postgresql":
        try:
            return PostgreSQLQueryStore()
        except Exception as e:
            print(f"[query_store] PostgreSQL connection failed: {e}, falling back to SQLite")
            return SQLiteQueryStore()
    return SQLiteQueryStore()
