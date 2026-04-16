# api/main.py
# FastAPI application for Studio Knowledge API

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import query, ingest, index, faq, cache, jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: pre-warm services
    print("[API] Starting Studio Knowledge API...")
    
    # Log which services are being used
    import config
    embed_type = "external" if config.USE_EXTERNAL_EMBED == "true" else "local"
    llm_type = "external" if config.USE_EXTERNAL_LLM == "true" else "local"
    print(f"[API] Using embedding: {embed_type} - {config.EMBED_SERVER_URL if embed_type == 'external' else config.EMBED_MODEL}")
    print(f"[API] Using LLM: {llm_type} - {config.LLM_SERVER_URL if llm_type == 'external' else config.OLLAMA_BASE_URL} ({config.LLM_MODEL if llm_type == 'external' else config.OLLAMA_MODEL})")
    
    # PRE-WARM: Load embedding model at startup to avoid cold start
    from services.rag_service import get_rag_service
    rag = get_rag_service()
    rag.prewarm()
    
    # Start job queue worker
    from services.job_queue import get_job_queue
    get_job_queue().start()
    
    yield
    
    # Shutdown
    print("[API] Shutting down...")
    get_job_queue().stop()


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
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(index.router, prefix="/index", tags=["Index"])
app.include_router(faq.router, prefix="/faq", tags=["FAQ"])
app.include_router(cache.router, prefix="/cache", tags=["Cache"])


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    from services.rag_service import get_rag_service
    from services.cache import get_query_cache
    from services.query_logger import get_query_logger
    import config

    rag = get_rag_service()
    cache = get_query_cache()
    logger = get_query_logger()

    # Embedding model info
    embedding_info = {
        "external": config.USE_EXTERNAL_EMBED == "true",
        "url": config.EMBED_SERVER_URL if config.USE_EXTERNAL_EMBED == "true" else config.EMBED_MODEL,
    }

    # LLM model info
    llm_info = {
        "external": config.USE_EXTERNAL_LLM == "true",
        "url": config.LLM_SERVER_URL if config.USE_EXTERNAL_LLM == "true" else config.OLLAMA_BASE_URL,
        "model": config.LLM_MODEL if config.USE_EXTERNAL_LLM == "true" else config.OLLAMA_MODEL,
    }

    return {
        "status": "ok",
        "warmed": rag.warmed,
        "embedding": embedding_info,
        "llm": llm_info,
        "index_loaded": rag.index_loaded,
        "index_stats": rag.index_stats,
        "cache_stats": cache.get_stats(),
        "query_count": logger.get_query_count()
    }
