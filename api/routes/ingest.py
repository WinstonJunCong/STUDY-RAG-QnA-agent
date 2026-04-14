# api/routes/ingest.py
# Ingest endpoint for rebuilding the index

from fastapi import APIRouter, HTTPException
from api.models import IngestRequest, IngestResponse
from services.rag_service import get_rag_service

router = APIRouter()


@router.post("", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    """Rebuild the index from documents."""
    rag = get_rag_service()

    try:
        result = rag.ingest(
            text_folders=request.text_folders,
            force_rebuild=request.force_rebuild or False
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {str(e)}")

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Ingest failed"))

    return IngestResponse(
        status=result["status"],
        chunks=result["chunks"],
        documents=result.get("documents"),
        timing_ms=result["timing_ms"]
    )
