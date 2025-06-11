from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# TODO: Authentication Request Models
class UserRegister(BaseModel):
    """
    User registration request model.
    TODO: Add validation for:
    - Email format validation
    - Password strength requirements
    - Username constraints
    """
    email: EmailStr
    password: str
    username: str


class UserLogin(BaseModel):
    """
    User login request model.
    TODO: Support both email and username login
    """
    email: EmailStr
    password: str


class PasswordReset(BaseModel):
    """
    Password reset request model.
    TODO: Implement password reset flow
    """
    email: EmailStr


class PasswordChange(BaseModel):
    """
    Password change request model.
    TODO: Add current password verification
    """
    current_password: str
    new_password: str


# TODO: Authentication Response Models
class UserProfile(BaseModel):
    """
    User profile response model.
    TODO: Add user profile fields based on requirements
    """
    id: str
    email: str
    username: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class AuthResponse(BaseModel):
    """
    Authentication response model.
    TODO: Decide token structure with Supabase integration
    """
    user: UserProfile
    access_token: Optional[str] = None  # Might not be needed with Supabase
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """
    Token refresh response model.
    TODO: Implement if custom token refresh is needed
    """
    access_token: str
    token_type: str = "bearer"


# TODO: Error Response Models
class AuthError(BaseModel):
    """
    Authentication error response model.
    TODO: Standardize error responses
    """
    detail: str
    error_code: Optional[str] = None


class ValidationError(BaseModel):
    """
    Validation error response model.
    TODO: Handle field-specific validation errors
    """
    field: str
    message: str 