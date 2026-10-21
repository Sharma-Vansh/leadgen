"""
LeadGen Module 3: Backend REST API & AI Matching Engine
FastAPI application entrypoint serving auth, candidate profile verification,
and AI-driven matched job feeds.
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from module_2_database_and_ingestion.db.base import Base
from module_2_database_and_ingestion.db.session import get_engine, check_db_health
# Import all models to ensure metadata registration
import module_2_database_and_ingestion.db.models
import module_3_backend_and_matching.models
from module_3_backend_and_matching.config import settings
from module_3_backend_and_matching.routes import auth_router, profile_router, feed_router
from module_3_backend_and_matching.matcher.embedder import SENTENCE_TRANSFORMER_ACTIVE

logger = logging.getLogger("LeadGenAPI")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager for connection warmup and table creation."""
    logger.info(f"[API] Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # Initialize engine and ensure tables exist
    engine = get_engine()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("[API] Database schema checked and synchronized.")
    except Exception as e:
        logger.warning(f"[API] Table synchronization warning: {e}")

    yield

    logger.info("[API] Shutting down LeadGen API.")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "LeadGen Core REST API & AI Matching Engine.\n\n"
        "Connects candidate profiles with 388+ scraped job sources via "
        "hybrid semantic scoring, skill-gap analysis, and hard eligibility filtering."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route Registrations
app.include_router(auth_router)
app.include_router(profile_router, prefix=settings.API_PREFIX)
app.include_router(feed_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["System"])
async def root():
    """Root metadata endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "documentation": "/docs",
        "embedder": "SentenceTransformer (all-MiniLM-L6-v2)" if SENTENCE_TRANSFORMER_ACTIVE else "Deterministic 384-Dim Projector"
    }


@app.get("/health", tags=["System"])
async def health_check():
    """System and database liveness health check."""
    db_ok = await check_db_health()
    status_str = "healthy" if db_ok else "degraded"
    return JSONResponse(
        status_code=200 if db_ok else 503,
        content={
            "status": status_str,
            "database_connected": db_ok,
            "ai_embedder_active": True,
            "ai_engine": "all-MiniLM-L6-v2" if SENTENCE_TRANSFORMER_ACTIVE else "Deterministic 384-Dim Projector"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
