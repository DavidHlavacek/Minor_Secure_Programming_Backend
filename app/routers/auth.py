from fastapi import APIRouter, Depends, HTTPException, status
from app.models.auth import (
    UserRegister, UserLogin, UserProfile, AuthResponse, 
    PasswordReset, PasswordChange, AuthError
)
from app.core.security import get_current_user, get_current_active_user, validate_password
from app.core.database import get_db
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserRegister, db = Depends(get_db)):
    """
    Register a new user.
    Uses AuthService for business logic and Supabase integration.
    """
    auth_service = AuthService(db)
    
    # TODO: Implement with AuthService
    # return await auth_service.register_user(user_data)
    
    # Placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User registration not implemented yet - use AuthService"
    )


@router.post("/login", response_model=AuthResponse)
async def login_user(credentials: UserLogin, db = Depends(get_db)):
    """
    Authenticate user and return access token.
    TODO: Implement user authentication with Supabase:
    - Validate credentials
    - Authenticate with Supabase Auth
    - Return user profile and token
    """
    # Placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User login not implemented yet"
    )


@router.post("/logout")
async def logout_user(current_user = Depends(get_current_user)):
    """
    Logout current user.
    TODO: Implement logout with Supabase:
    - Invalidate current session
    - Clear user tokens
    """
    # Placeholder implementation
    return {"message": "Logout not implemented yet"}


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user = Depends(get_current_active_user)):
    """
    Get current user profile.
    TODO: Return authenticated user's profile information
    """
    # Placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get user profile not implemented yet"
    )


@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    profile_data: dict,  # TODO: Create proper update schema
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """
    Update current user profile.
    TODO: Implement profile update:
    - Validate update data
    - Update user in database
    - Return updated profile
    """
    # Placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update user profile not implemented yet"
    )


@router.post("/password/reset")
async def request_password_reset(reset_data: PasswordReset, db = Depends(get_db)):
    """
    Request password reset.
    TODO: Implement password reset flow:
    - Validate email
    - Send reset email via Supabase
    - Handle reset token generation
    """
    # Placeholder implementation
    return {"message": "Password reset not implemented yet"}


@router.post("/password/change")
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """
    Change user password.
    TODO: Implement password change:
    - Verify current password
    - Validate new password
    - Update password in Supabase
    """
    # Placeholder implementation
    return {"message": "Password change not implemented yet"}


@router.post("/refresh")
async def refresh_token(current_user = Depends(get_current_user)):
    """
    Refresh access token.
    TODO: Implement token refresh if needed (might not be required with Supabase)
    """
    # Placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented yet"
    ) 