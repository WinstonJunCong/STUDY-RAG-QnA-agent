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
    sources: list[str]
    timing_ms: int
    cache_hit: bool = False
    hit_type: Optional[str] = None
    job_id: Optional[str] = None


# --- Ingest ---
class IngestRequest(BaseModel):
    text_folders: Optional[List[str]] = None
    force_rebuild: Optional[bool] = False


class IngestResponse(BaseModel):
    status: str
    chunks: int = 0
    documents: Optional[int] = None
    timing_ms: int = 0
    message: Optional[str] = None
    job_id: Optional[str] = None


# --- Jobs ---
class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    source: str
    file_path: Optional[str] = None
    progress: int
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class JobListResponse(BaseModel):
    jobs: List[JobStatusResponse]
    count: int


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
