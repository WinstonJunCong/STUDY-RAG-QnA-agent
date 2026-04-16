# api/routes/query.py
# Query endpoint with cache support and async processing

from fastapi import APIRouter, HTTPException
from api.models import QueryRequest, QueryResponse
from services.rag_service import get_rag_service
from services.cache import get_query_cache
from services.query_logger import get_query_logger

router = APIRouter()


@router.post("", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Ask a question against the knowledge base.
    Returns job_id for async processing.
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    print(f"[query] API received: {request.question[:50]}...")

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
            hit_type=cached.get("hit_type", "exact"),
            job_id=None
        )

    # Queue async query job
    try:
        result = rag.query(request.question, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    # Log the query
    logger.log_query(
        request.question,
        answer=None,  # Will be filled when job completes
        hit_cache=False
    )

    # Cache the result (when job completes, will need to update this)
    # For now, return job_id so client can poll for results
    return QueryResponse(
        answer="",
        sources=[],
        timing_ms=0,
        cache_hit=False,
        job_id=result["job_id"]
    )


@router.post("/sync", response_model=QueryResponse)
async def query_sync(request: QueryRequest):
    """
    Ask a question synchronously (blocking).
    Use this for immediate results when you can't poll for job status.
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    print(f"[query] Sync API received: {request.question[:50]}...")

    rag = get_rag_service()
    cache = get_query_cache()
    logger = get_query_logger()

    # Try cache first
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
            hit_type=cached.get("hit_type", "exact"),
            job_id=None
        )

    # Process synchronously
    try:
        result = rag.query_sync(request.question, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

    # Log and cache
    logger.log_query(
        request.question,
        answer=result["answer"],
        hit_cache=False
    )

    cache.set(
        request.question,
        result["answer"],
        result["sources"]
    )

    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        timing_ms=result["timing_ms"],
        cache_hit=False,
        job_id=None
    )
