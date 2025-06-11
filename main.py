"""
Gamer CV API - Main Application Entry Point
A secure FastAPI backend for the Gamer CV mobile application.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.core.config import get_settings
from app.core.database import init_db, close_db, get_database
from app.api.v1.api import api_router

# Load environment variables
load_dotenv()

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    try:
        await init_db()
        print("✅ Database connection established")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    await close_db()
    print("🔌 Database connection closed")


# Create FastAPI application
app = FastAPI(
    title="Gamer CV API",
    description="A secure backend API for aggregating and managing gaming statistics",
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Gamer CV API is running!",
        "version": settings.version,
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    db = await get_database()
    db_healthy = await db.health_check()
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "gamer-cv-api",
        "version": settings.version,
        "database": "connected" if db_healthy else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
