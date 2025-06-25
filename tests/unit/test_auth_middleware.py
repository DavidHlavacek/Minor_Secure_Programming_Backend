import pytest
import jwt
import time
import json
from unittest.mock import patch, Mock, AsyncMock
from fastapi import HTTPException
from app.middleware.auth_middleware import (
    JWTValidator, 
    get_current_user, 
    get_optional_user,
    HTTPAuthorizationCredentials
)

# Sample JWK for testing
SAMPLE_JWK = {
    "kid": "test-key-id",
    "kty": "RSA",
    "alg": "RS256",
    "use": "sig",
    "n": "xnAFJwQQjS8Ksh0aHjzZKdgGxL5PmZLx8eY6B7BkL-uZ9EP9HFr2Jg9-1ixETACPMAIJMCA_egpiFSB_8YjItLjKTLJgBVj-vSMhUWDhQw5e0Pwj-SkJcoToZPf2gGQ_CNpZFyIQ6IT7Ke0gszJkfQPjjFWtbO9q-9SfZr9XDcNGn3xPUqzSjFfSwxTp5BHlFwFYPiUh3WnDJbR2HkdXfK-rs6UK2PAN4-nhMmYzKrHgKN-lO7DUmpJx3YAB5MnUxRKvbUBZ4LkNkK_ER0hJ1cu7GVF-XdRAlEpxwQQ-NG-CvZJsTXk8YDcFxLNDQYcd8vJclW-5_4ax0NbTOQ",
    "e": "AQAB"
}

# Sample token parts
SAMPLE_HEADER = {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "test-key-id"
}

SAMPLE_PAYLOAD = {
    "sub": "user123",
    "email": "test@example.com",
    "role": "user",
    "exp": int(time.time()) + 3600,  # 1 hour from now
    "iss": "https://nevvbfvsrqertmwgvhlw.supabase.co/auth/v1"
}

# Create a sample token (not actually valid, just for structure testing)
def create_sample_token():
    header = base64url_encode_json(SAMPLE_HEADER)
    payload = base64url_encode_json(SAMPLE_PAYLOAD)
    # In real tests we would sign this properly
    return f"{header}.{payload}.fake_signature"

def base64url_encode_json(data):
    """Helper function to base64url encode JSON data"""
    json_str = json.dumps(data).encode()
    import base64
    return base64.urlsafe_b64encode(json_str).decode().rstrip("=")


@pytest.fixture
def mock_jwks_response():
    """Mock response for JWKS endpoint"""
    return {"keys": [SAMPLE_JWK]}


@pytest.mark.asyncio
async def test_fetch_jwks_success(mock_jwks_response):
    """Test successful JWKS fetching"""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = mock_jwks_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        keys = await JWTValidator.fetch_jwks()
        
        assert len(keys) == 1
        assert keys[0]["kid"] == "test-key-id"
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_jwks_caching(mock_jwks_response):
    """Test that JWKS caching works"""
    with patch("requests.get") as mock_get:
        # First call
        mock_response = Mock()
        mock_response.json.return_value = mock_jwks_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        keys1 = await JWTValidator.fetch_jwks()
        assert len(keys1) == 1
        
        # Second call should use cache
        keys2 = await JWTValidator.fetch_jwks()
        assert len(keys2) == 1
        
        # Request should only be made once
        mock_get.assert_called_once()


def test_decode_token_header():
    """Test decoding token header"""
    token = create_sample_token()
    
    header = JWTValidator.decode_token_header(token)
    
    assert header["alg"] == "RS256"
    assert header["typ"] == "JWT"
    assert header["kid"] == "test-key-id"


def test_decode_token_header_invalid():
    """Test decoding invalid token header"""
    with pytest.raises(HTTPException) as exc_info:
        JWTValidator.decode_token_header("invalid.token")
    
    assert exc_info.value.status_code == 401
    assert "Invalid token format" in exc_info.value.detail


@pytest.mark.asyncio
async def test_verify_token(mock_jwks_response):
    """Test token verification success path"""
    token = create_sample_token()
    
    # We need to mock the actual verification since we're not using real signatures
    with patch("app.middleware.auth_middleware.JWTValidator.fetch_jwks") as mock_fetch:
        mock_fetch.return_value = mock_jwks_response["keys"]
        
        with patch("app.middleware.auth_middleware.JWTValidator.verify_token_signature") as mock_verify:
            mock_verify.return_value = True
            
            # For simplicity, mock jwt.decode to return our sample payload
            with patch("jwt.decode") as mock_decode:
                mock_decode.return_value = SAMPLE_PAYLOAD
                
                payload = await JWTValidator.verify_token(token)
                
                assert payload["sub"] == "user123"
                assert payload["email"] == "test@example.com"
                assert payload["role"] == "user"
                assert "exp" in payload


@pytest.mark.asyncio
async def test_verify_token_expired():
    """Test handling of expired tokens"""
    # Create a token with expired payload
    expired_payload = SAMPLE_PAYLOAD.copy()
    expired_payload["exp"] = int(time.time()) - 3600  # 1 hour ago
    
    with patch("jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")
        
        with pytest.raises(HTTPException) as exc_info:
            await JWTValidator.verify_token("expired.token.signature")
        
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_token_invalid():
    """Test handling of invalid tokens"""
    with patch("jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")
        
        with pytest.raises(HTTPException) as exc_info:
            await JWTValidator.verify_token("invalid.token.signature")
        
        assert exc_info.value.status_code == 401
        assert "invalid" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_current_user_success():
    """Test successful user extraction"""
    # Create mock credentials
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=create_sample_token())
    
    with patch("app.middleware.auth_middleware.JWTValidator.verify_token") as mock_verify:
        mock_verify.return_value = SAMPLE_PAYLOAD
        
        user = await get_current_user(credentials)
        
        assert user["user_id"] == "user123"
        assert user["email"] == "test@example.com"
        assert user["role"] == "user"


@pytest.mark.asyncio
async def test_get_current_user_missing_credentials():
    """Test handling of missing credentials"""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(None)
    
    assert exc_info.value.status_code == 401
    assert "Authentication required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_optional_user_success():
    """Test successful optional user extraction"""
    # Create mock credentials
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=create_sample_token())
    
    with patch("app.middleware.auth_middleware.JWTValidator.verify_token") as mock_verify:
        mock_verify.return_value = SAMPLE_PAYLOAD
        
        user = await get_optional_user(credentials)
        
        assert user["user_id"] == "user123"
        assert user["email"] == "test@example.com"
        assert user["role"] == "user"


@pytest.mark.asyncio
async def test_get_optional_user_missing_credentials():
    """Test handling of missing credentials for optional user"""
    user = await get_optional_user(None)
    
    assert user is None


@pytest.mark.asyncio
async def test_get_optional_user_invalid_token():
    """Test handling of invalid token for optional user"""
    # Create mock credentials
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token")
    
    with patch("app.middleware.auth_middleware.JWTValidator.verify_token") as mock_verify:
        mock_verify.side_effect = HTTPException(status_code=401, detail="Invalid token")
        
        user = await get_optional_user(credentials)
        
        assert user is None
