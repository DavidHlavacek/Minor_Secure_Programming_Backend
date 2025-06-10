"""
Input Validation Schemas

Secure input validation for all user inputs.
Protects against injection attacks, XSS, and malformed data.
"""

import re
from typing import Optional, Dict, Any
from pydantic import BaseModel, validator, Field


# Validation Patterns
PATTERNS = {
    "username": r"^[a-zA-Z0-9_-]{3,30}$",
    "game_name": r"^[a-zA-Z0-9\s:'-]{2,100}$",
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "password": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,128}$"
}

# Blacklisted patterns (SQL injection, XSS, etc.)
SECURITY_BLACKLIST = [
    r"(<script|</script>)",  # XSS
    r"(union\s+select|select\s+\*\s+from)",  # SQL injection
    r"(drop\s+table|delete\s+from)",  # SQL injection
    r"(javascript:|data:|vbscript:)",  # Protocol injection
    r"(\.\./|\.\.\\)",  # Path traversal
]


class SecureUserInput(BaseModel):
    """Base class for secure user input validation"""
    
    @classmethod
    def validate_against_blacklist(cls, value: str) -> str:
        """Check input against security blacklist"""
        if not isinstance(value, str):
            return value
            
        for pattern in SECURITY_BLACKLIST:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError(f"Input contains potentially malicious content")
        return value


class SecureGameInput(SecureUserInput):
    """Validation for game-related inputs"""
    
    game_name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=30)
    category: str = Field(..., regex=r"^(MOBA|FPS|RPG|Strategy|Sports)$")
    
    @validator("game_name")
    def validate_game_name(cls, v):
        v = cls.validate_against_blacklist(v)
        if not re.match(PATTERNS["game_name"], v):
            raise ValueError("Game name contains invalid characters")
        return v.strip()
    
    @validator("username")
    def validate_username(cls, v):
        v = cls.validate_against_blacklist(v)
        if not re.match(PATTERNS["username"], v):
            raise ValueError("Username must be 3-30 characters, alphanumeric, _, - only")
        return v.strip()


class SecureAuthInput(SecureUserInput):
    """Validation for authentication inputs"""
    
    email: str = Field(..., min_length=5, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator("email")
    def validate_email(cls, v):
        v = cls.validate_against_blacklist(v)
        if not re.match(PATTERNS["email"], v):
            raise ValueError("Invalid email format")
        return v.lower().strip()
    
    @validator("password")
    def validate_password(cls, v):
        # Don't check blacklist for passwords (might contain legitimate special chars)
        if not re.match(PATTERNS["password"], v):
            raise ValueError("Password must be 8-128 chars with uppercase, lowercase, and number")
        return v


class SecureAPIParams(SecureUserInput):
    """Validation for external API parameters"""
    
    region: Optional[str] = Field(None, regex=r"^[a-z0-9]{2,10}$")
    platform: Optional[str] = Field(None, regex=r"^(pc|xbox|psn|steam|uplay)$")
    queue_type: Optional[str] = Field(None, max_length=50)
    
    @validator("*", pre=True)
    def validate_all_strings(cls, v):
        if isinstance(v, str):
            return cls.validate_against_blacklist(v)
        return v


# Validation Functions
def validate_file_upload(filename: str, max_size_mb: int = 5) -> bool:
    """
    Validate file uploads for security
    
    TODO: Implement:
    - File extension whitelist
    - MIME type validation
    - Size limits
    - Virus scanning
    """
    return True


def sanitize_html_input(html_content: str) -> str:
    """
    Sanitize HTML content to prevent XSS
    
    TODO: Implement:
    - Remove dangerous tags
    - Escape special characters
    - Whitelist safe HTML
    """
    return html_content


def validate_json_structure(data: Dict[str, Any], max_depth: int = 10) -> bool:
    """
    Validate JSON structure to prevent attacks
    
    TODO: Implement:
    - Depth limits
    - Key validation
    - Value type checking
    """
    return True 