"""
Gamer CV API - Main Application Entry Point
A secure FastAPI backend for the Gamer CV mobile application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.api.v1.api import api_router as api_v1_router

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Gamer CV API",
    description="A secure backend API for aggregating and managing gaming statistics",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
allowed_origins = ["*"]  # Allow all origins for development

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API router with all endpoints
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Gamer CV API is running!",
        "version": "0.1.0",
        "status": "healthy",
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
    )
