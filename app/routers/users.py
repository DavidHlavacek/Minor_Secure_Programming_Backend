from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List
from app.models.auth import UserProfile
from app.models.users import UserUpdate, UserSettings, UserStatsOverview
from app.core.security import get_current_active_user
from app.core.database import get_database
from app.services.users_service import UsersService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Get current user's profile information.
    """
    # TODO: Use UsersService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get user profile not implemented yet"
    )


@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    profile_data: UserUpdate,
    current_user = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Update current user's profile information.
    
    Flow:
    1. Validate update data
    2. Update user in database
    3. Return updated profile
    """
    # TODO: Use UsersService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update user profile not implemented yet"
    )


@router.get("/me/settings", response_model=UserSettings)
async def get_user_settings(
    current_user = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Get user's application settings and preferences.
    """
    # TODO: Use UsersService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get user settings not implemented yet"
    )


@router.put("/me/settings", response_model=UserSettings)
async def update_user_settings(
    settings_data: UserSettings,
    current_user = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Update user's application settings and preferences.
    """
    # TODO: Use UsersService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Update user settings not implemented yet"
    )


@router.get("/me/overview", response_model=UserStatsOverview)
async def get_user_overview(
    current_user = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Get user's gaming overview and aggregated statistics.
    
    Returns:
    - Total games added
    - Favorite categories
    - Recent activity
    - Overall stats summary
    """
    # TODO: Use UsersService and StatsService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get user overview not implemented yet"
    )


@router.delete("/me")
async def delete_user_account(
    current_user = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Delete current user's account and all associated data.
    
    WARNING: This is irreversible!
    
    Flow:
    1. Delete all user's games
    2. Delete all user's stats
    3. Delete user profile
    4. Revoke all tokens
    """
    # TODO: Use UsersService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Account deletion not implemented yet"
    )


@router.get("/me/activity")
async def get_user_activity(
    limit: int = 10,
    current_user = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Get user's recent activity log.
    
    Returns:
    - Recent games added
    - Recent stats updates
    - Login history
    """
    # TODO: Implement activity tracking
    return {
        "activities": [],
        "total": 0,
        "limit": limit
    } 