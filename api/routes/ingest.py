# api/routes/ingest.py
# Ingest endpoint with async job processing

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from api.models import IngestRequest, IngestResponse
from services.rag_service import get_rag_service
from services.job_queue import get_job_queue
import config

router = APIRouter()


@router.post("", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    """
    Start async ingestion from configured folders.
    Returns job_id immediately, processing happens in background.
    """
    # Use config defaults if not specified or invalid
    folders = request.text_folders
    if not folders or not all(isinstance(f, str) and f for f in folders):
        folders = config.TEXT_FOLDERS
    
    job_queue = get_job_queue()
    
    # Create job
    job_id = job_queue.create_job(
        source="folder",
        text_folders=folders,
        force_rebuild=request.force_rebuild or False
    )
    
    # Job is queued, return immediately
    return IngestResponse(
        status="queued",
        job_id=job_id,
        message="Ingestion job created and queued"
    )


@router.post("/upload", response_model=IngestResponse)
async def upload_and_ingest(
    file: UploadFile = File(...),
    force_rebuild: bool = Form(False)
):
    """
    Upload a document file and queue for ingestion.
    Supported formats: .txt, .md, .pdf, .docx, .html
    """
    # Validate file extension
    allowed_extensions = {".txt", ".md", ".pdf", ".docx", ".html"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Check file size
    file_size_limit = 50 * 1024 * 1024  # 50MB
    contents = await file.read()
    
    if len(contents) > file_size_limit:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {file_size_limit // (1024*1024)}MB"
        )
    
    # Create uploads directory
    import uuid
    job_id = str(uuid.uuid4())[:8]
    safe_filename = f"{job_id}_{file.filename}"
    upload_dir = Path("./data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / safe_filename
    
    # Write file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Queue ingestion job
    job_queue = get_job_queue()
    job_id = job_queue.create_job(
        source="upload",
        file_path=str(file_path),
        force_rebuild=force_rebuild
    )
    
    return IngestResponse(
        status="queued",
        job_id=job_id,
        message=f"File {file.filename} uploaded and queued for ingestion"
    )


@router.get("/types")
async def get_supported_types():
    """Get list of supported file types for ingestion."""
    return {
        "types": [
            {"extension": ".txt", "name": "Plain Text"},
            {"extension": ".md", "name": "Markdown"},
            {"extension": ".pdf", "name": "PDF Document"},
            {"extension": ".docx", "name": "Word Document"},
            {"extension": ".html", "name": "HTML Page"}
        ],
        "max_size_mb": 50
    }
