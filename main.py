"""
Gamer CV API - Main Application Entry Point
A secure FastAPI backend for the Gamer CV mobile application.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import time

from app.api.v1.api import api_router as api_v1_router
from app.middleware.security import SecurityMiddleware

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Gamer CV API",
    description="A secure backend API for aggregating and managing gaming statistics",
    version="0.1.0",
    docs_url="/docs" if os.getenv("DEBUG", "False").lower() == "true" else None,  # Only enable in debug mode
    redoc_url="/redoc" if os.getenv("DEBUG", "False").lower() == "true" else None, # Only enable in debug mode
    # Enhanced security configurations
    openapi_url="/openapi.json" if os.getenv("DEBUG", "False").lower() == "true" else None,
)

# Configure CORS with restricted origins for production
allowed_origins = [
    "https://minor-secure-programming-frontend.netlify.app",  # Production frontend URL
    "https://nevvbfvsrqertmwgvhlw.supabase.co",              # Supabase domain
    "https://minor-secure-programming-backend.onrender.com"  # Backend URL itself (for API docs)
]

# Add development origins if in debug mode
if os.getenv("DEBUG", "False").lower() == "true":
    # Only allow specific origins even in development
    allowed_origins.extend([
        "http://localhost:8081",   # Dev frontend
        "http://10.0.2.2:8081",   # Android emulator to localhost
        "http://127.0.0.1:8081",   # Alternative localhost
        "http://10.0.2.2:8000",   # Android app connected to backend on same port
        "http://localhost:8000",   # Local app to local backend
        "http://localhost:*",      # Any local development
        "http://10.0.2.2:*"       # Any Android emulator to local
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    # Restrict methods to only what's needed
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    # Restrict headers to specific ones needed
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
    # Expose headers that might be needed by the frontend
    expose_headers=["Content-Length", "X-Content-Type-Options"],
    # Add maximum age to cache preflight requests
    max_age=600
)

# Add security middleware to the application
# Exclude API docs from rate limiting
exclude_paths = ["/docs", "/redoc", "/openapi.json", "/"]

# Consider trusted ips (like your development machine) to bypass rate limits
trusted_ips = []
if os.getenv("TRUSTED_IPS"):
    trusted_ips = os.getenv("TRUSTED_IPS").split(",")

# Add security middleware with rate limiting
app.add_middleware(
    SecurityMiddleware,
    rate_limit_requests=100,  # 100 requests per minute per IP
    rate_limit_window=60,     # 1 minute window
    exclude_paths=exclude_paths,
    trusted_ips=trusted_ips,
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Generate request ID for tracking
    request_id = f"{time.time()}-{os.urandom(4).hex()}"
    
    # Add request ID to request state for use in endpoints
    request.state.request_id = request_id
    
    # Get client IP and requested path
    client_host = request.client.host if request.client else "unknown"
    path = request.url.path
    method = request.method
    
    # Don't log sensitive data like passwords, tokens, etc.
    # Start timer for request duration
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Calculate request processing time
    process_time = time.time() - start_time
    
    # Add request ID to response headers for tracking
    response.headers["X-Request-ID"] = request_id
    
    # Log request info (sanitized) - no tokens or sensitive data
    # Security: Using structured logging format without sensitive data
    print(f"[REQUEST] {request_id} - {client_host} - {method} {path} - Status: {response.status_code} - Duration: {process_time:.4f}s")
    
    return response

# Include v1 API router with all endpoints
app.include_router(api_v1_router, prefix="/api/v1")

# Add global exception handler to prevent leaking sensitive information
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Get request ID if available
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Log the error with request ID but without potentially sensitive details
    print(f"[ERROR] {request_id} - Unhandled exception: {type(exc).__name__}")
    
    # Return generic error response without exposing internal details
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "request_id": request_id,
        },
    )


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
