"""
JWT Authentication Middleware

Implements JWT token validation for Supabase authentication tokens.
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, DecodeError
from jose import jwk
from jose.utils import base64url_decode
import os
from typing import Optional, Dict, Any, List, Union
import time
import json
import logging
import requests
from dotenv import load_dotenv

# Setup logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Security configuration
security = HTTPBearer(
    scheme_name="JWT",
    description="JWT authentication with Supabase token",
    auto_error=False  # Don't automatically raise errors for routes that don't require auth
)

# Supabase configuration
SUPABASE_PROJECT_ID = os.getenv("SUPABASE_PROJECT_ID", "nevvbfvsrqertmwgvhlw")
SUPABASE_JWKS_URL = f"https://{SUPABASE_PROJECT_ID}.supabase.co/auth/v1/jwks"

# Security settings
VERIFY_SIGNATURE = os.getenv("VERIFY_JWT_SIGNATURE", "True").lower() == "true"
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

# Cache JWKs to avoid excessive HTTP requests
JWKS_CACHE = {
    "keys": [],
    "last_updated": 0,
    "cache_duration": 3600  # Cache keys for 1 hour
}


class JWTValidator:
    """JWT Token validation for Supabase tokens"""
    
    @staticmethod
    async def fetch_jwks() -> List[Dict]:
        """Fetch JWKS from Supabase with caching"""
        current_time = time.time()
        
        # Return cached keys if they're still valid
        if (JWKS_CACHE["keys"] and 
            current_time - JWKS_CACHE["last_updated"] < JWKS_CACHE["cache_duration"]):
            return JWKS_CACHE["keys"]
            
        try:
            # Fetch fresh JWKS
            if DEBUG_MODE:
                logger.debug(f"Fetching JWKS from {SUPABASE_JWKS_URL}")
                
            response = requests.get(SUPABASE_JWKS_URL, timeout=5)
            response.raise_for_status()
            jwks = response.json()
            
            # Update cache
            JWKS_CACHE["keys"] = jwks.get("keys", [])
            JWKS_CACHE["last_updated"] = current_time
            
            return JWKS_CACHE["keys"]
        except requests.RequestException as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            # Fall back to cached keys if available
            if JWKS_CACHE["keys"]:
                logger.warning("Using cached JWKS due to fetch failure")
                return JWKS_CACHE["keys"]
            raise HTTPException(
                status_code=500,
                detail="Unable to verify authentication tokens"
            )
    
    @staticmethod
    def decode_token_header(token: str) -> Dict:
        """Decode the JWT header without verification"""
        try:
            # JWT format: header.payload.signature
            header_segment = token.split(".")[0]
            padded_header = header_segment + "=" * (-len(header_segment) % 4)
            header_data = base64url_decode(padded_header)
            return json.loads(header_data)
        except Exception as e:
            logger.error(f"Error decoding token header: {e}")
            raise HTTPException(
                status_code=401, 
                detail="Invalid token format"
            )
    
    @staticmethod
    def verify_token_signature(token: str, jwk_key: Dict) -> bool:
        """Verify JWT token signature using JWK"""
        try:
            # Split the JWT into parts
            header_segment, payload_segment, signature_segment = token.split(".")
            message = f"{header_segment}.{payload_segment}"
            
            # Decode the signature
            signature = base64url_decode(signature_segment)
            
            # Get the key for verification
            public_key = jwk.construct(jwk_key)
            
            # Verify signature
            return public_key.verify(message.encode(), signature)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    @staticmethod
    async def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify JWT token and return payload if valid
        
        Args:
            token: JWT token to verify
            
        Returns:
            Dict containing token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            # Initial decode without verification to extract claims
            payload = jwt.decode(
                token,
                options={"verify_signature": False},
                algorithms=["RS256"]
            )
            
            # Verify token hasn't expired
            if "exp" in payload and payload["exp"] < time.time():
                raise ExpiredSignatureError("Token has expired")
            
            # In debug mode or when verification is disabled, skip signature check
            if not VERIFY_SIGNATURE:
                if DEBUG_MODE:
                    logger.warning("Skipping JWT signature verification (not secure for production!)")
                return payload
            
            # For production, we need to verify the signature
            # Get the header to find the key ID (kid)
            token_header = JWTValidator.decode_token_header(token)
            kid = token_header.get("kid")
            
            if not kid:
                raise InvalidTokenError("No key ID found in token header")
            
            # Fetch JWKS
            jwks = await JWTValidator.fetch_jwks()
            matching_key = next((k for k in jwks if k.get("kid") == kid), None)
            
            if not matching_key:
                raise InvalidTokenError(f"No matching key found for kid: {kid}")
            
            # Verify signature
            if not JWTValidator.verify_token_signature(token, matching_key):
                raise InvalidTokenError("Invalid token signature")
            
            # Verify token issuer is Supabase
            issuer = payload.get("iss")
            if not issuer or not issuer.endswith(f"{SUPABASE_PROJECT_ID}.supabase.co"):
                raise InvalidTokenError(f"Invalid token issuer: {issuer}")
            
            return payload
            
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=401, 
                detail="Authentication token expired"
            )
        except DecodeError:
            raise HTTPException(
                status_code=401, 
                detail="Invalid authentication token format"
            )
        except InvalidTokenError as e:
            raise HTTPException(
                status_code=401, 
                detail=f"Invalid authentication token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=401, 
                detail="Authentication failed"
            )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Authorization credentials with Bearer token
        
    Returns:
        Dict containing user information from token
        
    Raises:
        HTTPException: If no valid credentials provided or invalid token
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    # Validate token
    payload = await JWTValidator.verify_token(credentials.credentials)
    
    # Extract user info from payload
    if "sub" not in payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid user information in token"
        )
        
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email", ""),
        "role": payload.get("role", "user"),
        "exp": payload.get("exp", 0),
        # Add any other relevant user info from token
    }


# Optional dependency for routes that don't require authentication but can use it
async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, otherwise return None
    
    Args:
        credentials: HTTP Authorization credentials with Bearer token
        
    Returns:
        Dict containing user information from token or None if not authenticated
    """
    if not credentials:
        return None
        
    try:
        # Validate token
        payload = await JWTValidator.verify_token(credentials.credentials)
        
        # Extract user info from payload
        if "sub" not in payload:
            return None
            
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email", ""),
            "role": payload.get("role", "user"),
            "exp": payload.get("exp", 0),
            # Add any other relevant user info from token
        }
    except HTTPException:
        return None
