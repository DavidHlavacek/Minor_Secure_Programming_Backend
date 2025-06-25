"""
Security middleware for FastAPI backend
Implements rate limiting, security headers, and other security features
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from typing import Dict, List, Tuple
import ipaddress

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app: ASGIApp, 
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,
        exclude_paths: List[str] = None,
        trusted_ips: List[str] = None
    ):
        """
        Initialize security middleware with configuration
        :param app: ASGI app
        :param rate_limit_requests: Maximum number of requests per window
        :param rate_limit_window: Time window in seconds
        :param exclude_paths: List of paths to exclude from rate limiting
        :param trusted_ips: List of trusted IP addresses or networks that bypass rate limits
        """
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.request_history: Dict[str, List[float]] = {}
        self.exclude_paths = exclude_paths or []
        self.trusted_networks = []

        # Convert trusted IPs to network objects for comparison
        if trusted_ips:
            for ip in trusted_ips:
                try:
                    if '/' in ip:
                        self.trusted_networks.append(ipaddress.ip_network(ip, strict=False))
                    else:
                        self.trusted_networks.append(ipaddress.ip_address(ip))
                except ValueError:
                    continue  # Skip invalid IP addresses
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request through security middleware
        :param request: FastAPI request
        :param call_next: Next middleware to call
        :return: Response
        """
        # Get client IP address
        client_ip = self._get_client_ip(request)
        
        # Skip rate limiting for trusted IPs or excluded paths
        if not self._is_rate_limited(request, client_ip):
            response = await call_next(request)
            return self._add_security_headers(response)
        
        # Check rate limit
        if not self._check_rate_limit(client_ip):
            # Return 429 Too Many Requests if rate limit exceeded
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
            
        try:
            # Process the request
            response = await call_next(request)
            # Add security headers to response
            return self._add_security_headers(response)
        except Exception as e:
            # Re-raise exception, handled by FastAPI's exception handlers
            raise e
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request headers or connection info"""
        # Check for forwarded IP (when behind proxy or load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Use the first IP in the list if multiple are present
            return forwarded.split(",")[0]
        # Fall back to direct client IP
        return request.client.host if request.client else "0.0.0.0"
    
    def _is_rate_limited(self, request: Request, client_ip: str) -> bool:
        """Check if request should be rate limited"""
        # Skip rate limiting for excluded paths
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return False
        
        # Skip rate limiting for trusted IPs
        try:
            ip_obj = ipaddress.ip_address(client_ip)
            for network in self.trusted_networks:
                if isinstance(network, ipaddress.IPv4Network) or isinstance(network, ipaddress.IPv6Network):
                    if ip_obj in network:
                        return False
                elif ip_obj == network:
                    return False
        except ValueError:
            pass  # If IP parsing fails, continue with rate limiting
            
        return True
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Check if the client has exceeded rate limits
        :return: True if within limit, False if exceeded
        """
        current_time = time.time()
        
        # Initialize client history if not exists
        if client_ip not in self.request_history:
            self.request_history[client_ip] = []
        
        # Remove timestamps outside the current window
        self.request_history[client_ip] = [
            ts for ts in self.request_history[client_ip] 
            if current_time - ts < self.rate_limit_window
        ]
        
        # Check if client exceeded rate limit
        if len(self.request_history[client_ip]) >= self.rate_limit_requests:
            return False
        
        # Add current request timestamp
        self.request_history[client_ip].append(current_time)
        return True
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response"""
        # Content-Security-Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "object-src 'none'; "
            "media-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self';"
        )
        
        # Other security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store, max-age=0"
        
        # Add Strict Transport Security header for HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response
