# api/routes/query.py
# Query endpoint with cache support

from fastapi import APIRouter, HTTPException
from api.models import QueryRequest, QueryResponse
from services.rag_service import get_rag_service
from services.cache import get_query_cache
from services.query_logger import get_query_logger

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Ask a question against the knowledge base."""
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    rag = get_rag_service()
    cache = get_query_cache()
    logger = get_query_logger()

    # Try cache first (exact match only for now)
    cached = cache.get(request.question)
    if cached:
        logger.log_query(
            request.question,
            answer=cached["answer"],
            hit_cache=True
        )
        return QueryResponse(
            answer=cached["answer"],
            sources=cached.get("sources", []),
            timing_ms=0,
            cache_hit=True,
            hit_type=cached.get("hit_type", "exact")
        )

    # Process via RAG service
    try:
        result = rag.query(request.question, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    # Log the query
    logger.log_query(
        request.question,
        answer=result["answer"],
        hit_cache=False
    )

    # Cache the result
    cache.set(
        request.question,
        result["answer"],
        result["sources"]
    )

    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        timing_ms=result["timing_ms"],
        cache_hit=False
    )
