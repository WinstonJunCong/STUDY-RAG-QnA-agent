# api/routes/cache.py
# Cache management endpoints

from fastapi import APIRouter
from api.models import CacheClearResponse
from services.cache import get_query_cache

router = APIRouter()


@router.delete("/clear", response_model=CacheClearResponse)
async def clear_cache():
    """Clear the query cache."""
    cache = get_query_cache()
    cache.clear()
    return CacheClearResponse(
        status="ok",
        message="Cache cleared"
    )
