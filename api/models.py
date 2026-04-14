# api/models.py
# Pydantic models for API request/response schemas

from typing import Optional, List
from pydantic import BaseModel


# --- Query ---
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    timing_ms: int
    cache_hit: bool = False
    hit_type: Optional[str] = None


# --- Ingest ---
class IngestRequest(BaseModel):
    text_folders: Optional[List[str]] = None
    force_rebuild: Optional[bool] = False


class IngestResponse(BaseModel):
    status: str
    chunks: int = 0
    documents: Optional[int] = None
    timing_ms: int
    message: Optional[str] = None


# --- Index ---
class IndexStatusResponse(BaseModel):
    index_loaded: bool
    chunk_count: int
    last_updated: Optional[str] = None


class IndexDeleteResponse(BaseModel):
    status: str


# --- FAQ ---
class FAQEntry(BaseModel):
    question: str
    answer: str
    source: Optional[str] = None


class FAQListResponse(BaseModel):
    entries: List[FAQEntry]
    count: int


class FAQGenerateRequest(BaseModel):
    min_count: Optional[int] = None
    similarity_threshold: Optional[float] = None


class FAQGenerateResponse(BaseModel):
    status: str
    drafts_count: int
    message: str


class FAQApproveResponse(BaseModel):
    status: str
    entries_count: int
    message: str


# --- Cache ---
class CacheClearResponse(BaseModel):
    status: str
    message: str


# --- Health ---
class HealthResponse(BaseModel):
    status: str
    index_loaded: bool
    index_stats: dict
    cache_stats: dict
    query_count: int
