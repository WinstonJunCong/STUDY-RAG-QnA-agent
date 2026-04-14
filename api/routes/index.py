# api/routes/index.py
# Index management endpoints

from fastapi import APIRouter
from api.models import IndexStatusResponse, IndexDeleteResponse
from services.rag_service import get_rag_service

router = APIRouter()


@router.get("/status", response_model=IndexStatusResponse)
async def get_status():
    """Get index status and statistics."""
    rag = get_rag_service()
    return IndexStatusResponse(
        index_loaded=rag.index_loaded,
        chunk_count=rag.index_stats.get("chunk_count", 0),
        last_updated=rag.index_stats.get("last_updated")
    )


@router.delete("", response_model=IndexDeleteResponse)
async def delete_index():
    """Clear the vector index."""
    rag = get_rag_service()
    rag.delete_index()
    return IndexDeleteResponse(status="deleted")
