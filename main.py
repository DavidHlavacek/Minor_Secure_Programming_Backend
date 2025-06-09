"""
Gamer Stats API - Main Application Entry Point
Simple FastAPI backend for gaming statistics tracking with security features.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from app.routers import auth, games, stats
from app.core.database import init_db, close_db
from app.middleware import SecurityMiddleware, RateLimitMiddleware, AuditMiddleware
from app.core.security_config import get_security_settings

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    security_settings = get_security_settings()
    
    app = FastAPI(
        title="Gamer Stats API",
        description="Simple API for gaming statistics tracking with security features",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Security middleware (order matters!)
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(RateLimitMiddleware) 
    app.add_middleware(AuditMiddleware)
    
    # Configure CORS with security settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=security_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    
    # Include routers
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(games.router, prefix="/api/v1") 
    app.include_router(stats.router, prefix="/api/v1")
    
    return app


# Create application instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Gamer Stats API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "gamer-stats-api",
        "version": "1.0.0"
    }


@app.get("/security")
async def security_status():
    """Security configuration and compliance status"""
    from app.core.security_config import get_owasp_compliance_status
    return {
        "security_headers": "enabled",
        "rate_limiting": "enabled", 
        "audit_logging": "enabled",
        "input_validation": "enabled",
        "owasp_compliance": get_owasp_compliance_status()
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
        log_level="info"
    ) 