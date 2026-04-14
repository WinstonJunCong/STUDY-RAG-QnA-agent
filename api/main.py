# api/main.py
# FastAPI application for Studio Knowledge API

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import query, ingest, index, faq, cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nothing special needed - index loads lazily
    print("[API] Starting Studio Knowledge API...")
    yield
    # Shutdown
    print("[API] Shutting down...")


app = FastAPI(
    title="Studio Knowledge API",
    description="RAG API for 3D animation studio documentation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
app.include_router(index.router, prefix="/index", tags=["Index"])
app.include_router(faq.router, prefix="/faq", tags=["FAQ"])
app.include_router(cache.router, prefix="/cache", tags=["Cache"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    from services.rag_service import get_rag_service
    from services.cache import get_query_cache
    from services.query_logger import get_query_logger

    rag = get_rag_service()
    cache = get_query_cache()
    logger = get_query_logger()

    return {
        "status": "ok",
        "index_loaded": rag.index_loaded,
        "index_stats": rag.index_stats,
        "cache_stats": cache.get_stats(),
        "query_count": logger.get_query_count()
    }
