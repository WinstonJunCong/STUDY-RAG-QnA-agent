# services/job_queue.py
# Async job queue for ingestion tasks

import uuid
import threading
import time
from datetime import datetime
from typing import Optional
from enum import Enum

import config


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IngestionJob:
    """Represents an ingestion job."""
    
    def __init__(
        self,
        job_id: str,
        source: str,
        file_path: Optional[str] = None,
        text_folders: Optional[list[str]] = None,
        force_rebuild: bool = False,
        query_text: Optional[str] = None,
        top_k: Optional[int] = None
    ):
        self.job_id = job_id
        self.source = source
        self.file_path = file_path
        self.text_folders = text_folders
        self.force_rebuild = force_rebuild
        self.query_text = query_text
        self.top_k = top_k
        self.status = JobStatus.PENDING
        self.progress = 0
        self.result: Optional[dict] = None
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "source": self.source,
            "file_path": self.file_path,
            "query_text": self.query_text,
            "top_k": self.top_k,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class JobQueue:
    """In-memory job queue with background worker."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._jobs: dict[str, IngestionJob] = {}
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        self._initialized = True
    
    def create_job(
        self,
        source: str,
        file_path: Optional[str] = None,
        text_folders: Optional[list[str]] = None,
        force_rebuild: bool = False,
        query_text: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> str:
        """Create a new job."""
        job_id = str(uuid.uuid4())[:8]
        job = IngestionJob(
            job_id=job_id,
            source=source,
            file_path=file_path,
            text_folders=text_folders,
            force_rebuild=force_rebuild,
            query_text=query_text,
            top_k=top_k
        )
        
        with self._lock:
            self._jobs[job_id] = job
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[dict]:
        """Get job by ID."""
        with self._lock:
            job = self._jobs.get(job_id)
            return job.to_dict() if job else None
    
    def get_all_jobs(self) -> list[dict]:
        """Get all jobs."""
        with self._lock:
            return [job.to_dict() for job in self._jobs.values()]
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        with self._lock:
            job = self._jobs.get(job_id)
            if job and job.status == JobStatus.PENDING:
                job.status = JobStatus.CANCELLED
                return True
        return False
    
    def process_job(self, job: IngestionJob):
        """Process a job."""
        from services.rag_service import get_rag_service
        
        job.status = JobStatus.PROCESSING
        job.progress = 10
        
        try:
            rag = get_rag_service()
            
            if job.source == "query":
                job.progress = 20
                result = rag.query_sync(
                    question=job.query_text,
                    top_k=job.top_k
                )
                job.progress = 90
                job.result = result
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now()
                return
            
            if job.source == "folder":
                job.progress = 20
                result = rag.ingest(
                    text_folders=job.text_folders,
                    force_rebuild=job.force_rebuild
                )
            elif job.source == "upload":
                job.progress = 20
                # Import here to avoid circular imports
                from pipeline.index_builder import add_document_to_index
                
                # For now, we'll add the document file path
                result = add_document_to_index(job.file_path)
                
            elif job.source == "text":
                job.progress = 20
                # Text ingestion would need separate implementation
                result = {"status": "ok", "chunks": 0, "message": "Text ingestion not implemented"}
            else:
                raise ValueError(f"Unknown source: {job.source}")
            
            job.progress = 90
            job.result = result
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            
        except Exception as e:
            job.error = str(e)
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
    
    def _worker(self):
        """Background worker that processes jobs."""
        while self._running:
            with self._lock:
                pending_jobs = [
                    job for job in self._jobs.values()
                    if job.status == JobStatus.PENDING
                ]
                pending_jobs.sort(key=lambda j: j.created_at)
            
            if pending_jobs:
                job = pending_jobs[0]
                self.process_job(job)
            else:
                time.sleep(1)
    
    def start(self):
        """Start the background worker."""
        if not self._running:
            self._running = True
            self._worker_thread = threading.Thread(target=self._worker, daemon=True)
            self._worker_thread.start()
            print("[job_queue] Background worker started")
    
    def stop(self):
        """Stop the background worker."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
            print("[job_queue] Background worker stopped")
    
    def clear_completed(self, older_than_hours: int = 24):
        """Clear completed jobs older than N hours."""
        cutoff = datetime.now().timestamp() - (older_than_hours * 3600)
        
        with self._lock:
            to_remove = []
            for job_id, job in self._jobs.items():
                if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                    if job.completed_at and job.completed_at.timestamp() < cutoff:
                        to_remove.append(job_id)
            
            for job_id in to_remove:
                del self._jobs[job_id]


def get_job_queue() -> JobQueue:
    """Get singleton job queue."""
    return JobQueue()
