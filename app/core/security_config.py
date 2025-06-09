"""
Security Configuration

Centralized security settings and configurations.
"""

from typing import Dict, List
from pydantic import BaseModel


class SecuritySettings(BaseModel):
    """Security configuration settings"""
    
    # JWT Settings
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    jwt_refresh_expire_days: int = 7
    
    # Password Security
    password_min_length: int = 8
    password_max_length: int = 128
    password_hash_rounds: int = 12
    
    # Rate Limiting (requests per minute)
    rate_limit_auth: int = 5       # Login attempts
    rate_limit_api: int = 100      # General API calls
    rate_limit_stats: int = 30     # Stats refresh calls
    
    # Session Security
    session_timeout_minutes: int = 60
    max_concurrent_sessions: int = 3
    
    # Input Validation
    max_request_size_mb: int = 10
    max_json_depth: int = 10
    allowed_file_extensions: List[str] = [".jpg", ".png", ".gif"]
    
    # API Security
    require_https: bool = True
    cors_origins: List[str] = ["http://localhost:3000"]  # Mobile app
    
    # Audit & Monitoring
    log_all_requests: bool = True
    log_failed_auth: bool = True
    alert_threshold_failed_logins: int = 5
    
    # External API Security
    external_api_timeout: int = 30
    external_api_max_retries: int = 3
    
    # Data Protection
    encrypt_sensitive_data: bool = True
    data_retention_days: int = 365


# OWASP Top 10 Security Controls
OWASP_SECURITY_CONTROLS = {
    "A01_broken_access_control": {
        "description": "Broken Access Control",
        "controls": [
            "JWT token validation on all protected endpoints",
            "User-specific data access verification", 
            "Role-based access control",
            "Resource ownership validation"
        ],
        "implemented": False  # TODO: Implement
    },
    "A02_cryptographic_failures": {
        "description": "Cryptographic Failures", 
        "controls": [
            "Password hashing with bcrypt",
            "JWT token encryption",
            "HTTPS enforcement",
            "Sensitive data encryption at rest"
        ],
        "implemented": False  # TODO: Implement
    },
    "A03_injection": {
        "description": "Injection Attacks",
        "controls": [
            "Input validation and sanitization",
            "Parameterized queries (Supabase handles this)",
            "Output encoding",
            "Security blacklist patterns"
        ],
        "implemented": True   # ✅ Validation schemas created
    },
    "A04_insecure_design": {
        "description": "Insecure Design",
        "controls": [
            "Security by design principles",
            "Threat modeling",
            "Security review process",
            "Principle of least privilege"
        ],
        "implemented": False  # TODO: Implement
    },
    "A05_security_misconfiguration": {
        "description": "Security Misconfiguration", 
        "controls": [
            "Security headers implementation",
            "Error handling without information disclosure",
            "Secure default configurations",
            "Regular security updates"
        ],
        "implemented": True   # ✅ Security headers added
    },
    "A06_vulnerable_components": {
        "description": "Vulnerable and Outdated Components",
        "controls": [
            "Dependency vulnerability scanning",
            "Regular updates of dependencies",
            "Security advisory monitoring",
            "Component inventory tracking"
        ],
        "implemented": False  # TODO: Implement
    },
    "A07_identification_failures": {
        "description": "Identification and Authentication Failures",
        "controls": [
            "Strong password requirements",
            "Multi-factor authentication support",
            "Session management",
            "Brute force protection"
        ],
        "implemented": False  # TODO: Implement
    },
    "A08_software_integrity_failures": {
        "description": "Software and Data Integrity Failures",
        "controls": [
            "Code signing verification",
            "Secure CI/CD pipeline", 
            "Data integrity checks",
            "Secure update mechanisms"
        ],
        "implemented": False  # TODO: Implement
    },
    "A09_logging_monitoring_failures": {
        "description": "Security Logging and Monitoring Failures",
        "controls": [
            "Comprehensive audit logging",
            "Security event monitoring",
            "Incident response procedures",
            "Log integrity protection"
        ],
        "implemented": True   # ✅ Audit middleware created
    },
    "A10_server_side_request_forgery": {
        "description": "Server-Side Request Forgery (SSRF)",
        "controls": [
            "URL validation for external APIs",
            "Network segmentation",
            "Request filtering",
            "Timeout controls"
        ],
        "implemented": False  # TODO: Implement
    }
}


# Security Headers Configuration
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block", 
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}


# Rate Limiting Configuration
RATE_LIMITS = {
    "/api/v1/auth/login": "5/minute",
    "/api/v1/auth/register": "3/minute", 
    "/api/v1/games": "20/minute",
    "/api/v1/stats/refresh": "10/minute",
    "default": "100/minute"
}


def get_security_settings() -> SecuritySettings:
    """Get security settings instance"""
    return SecuritySettings()


def get_owasp_compliance_status() -> Dict[str, bool]:
    """Get OWASP Top 10 compliance status"""
    return {
        control_id: details["implemented"] 
        for control_id, details in OWASP_SECURITY_CONTROLS.items()
    } 