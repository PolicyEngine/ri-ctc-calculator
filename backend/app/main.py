"""FastAPI application for RI CTC Calculator."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.dataset import init_dataset_manager
from app.api.routes import household, aggregate, health

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup/shutdown)."""
    # Startup
    logger.info("🚀 Starting RI CTC Calculator API...")

    # Initialize and load dataset
    logger.info("Loading RI microsimulation dataset...")
    dataset_manager = init_dataset_manager()
    await dataset_manager.load()

    logger.info("✓ API ready to accept requests")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await dataset_manager.cleanup()
    logger.info("✓ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for calculating Rhode Island Child Tax Credit impacts",
    lifespan=lifespan,
)

# Configure CORS
cors_origins = settings.cors_origins.copy()
if settings.frontend_url:
    cors_origins.append(settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(
    household.router,
    prefix=settings.api_prefix,
    tags=["household"]
)
app.include_router(
    aggregate.router,
    prefix=settings.api_prefix,
    tags=["aggregate"]
)
app.include_router(
    health.router,
    prefix=settings.api_prefix,
    tags=["health"]
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
