from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Profile Update Models
class UserUpdate(BaseModel):
    """
    User profile update request model.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    preferred_language: Optional[str] = "en"


# User Settings Models
class UserSettings(BaseModel):
    """
    User application settings and preferences.
    """
    # Privacy Settings
    profile_public: bool = False
    stats_public: bool = False
    allow_friend_requests: bool = True
    
    # Notification Settings
    email_notifications: bool = True
    push_notifications: bool = True
    stats_update_notifications: bool = True
    weekly_summary: bool = True
    
    # App Preferences
    theme: str = "system"  # light, dark, system
    default_category: Optional[str] = None
    auto_refresh_stats: bool = True
    stats_refresh_interval: int = 3600  # seconds
    
    # Data Preferences
    data_retention_days: int = 365
    export_format: str = "json"  # json, csv


# User Stats Overview Models
class CategorySummary(BaseModel):
    """Summary for a specific game category"""
    category: str
    games_count: int
    total_playtime: Optional[float] = None
    last_updated: Optional[datetime] = None
    favorite_game: Optional[str] = None


class UserStatsOverview(BaseModel):
    """
    User's overall gaming statistics overview.
    """
    total_games: int
    total_categories: int
    account_created: datetime
    last_activity: Optional[datetime] = None
    
    # Category Breakdown
    categories: List[CategorySummary]
    favorite_category: Optional[str] = None
    
    # Activity Stats
    games_added_this_month: int = 0
    stats_updates_this_month: int = 0
    
    # Achievement-like Stats
    total_wins: Optional[int] = None
    total_losses: Optional[int] = None
    overall_win_rate: Optional[float] = None
    highest_rank_achieved: Optional[str] = None


# Activity Models
class ActivityItem(BaseModel):
    """Single activity item"""
    id: str
    type: str  # "game_added", "stats_updated", "achievement_unlocked"
    title: str
    description: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class UserActivity(BaseModel):
    """User activity log"""
    activities: List[ActivityItem]
    total: int
    page: int = 1
    per_page: int = 10


# Friend System Models (for future)
class FriendRequest(BaseModel):
    """Friend request model"""
    id: str
    from_user_id: str
    to_user_id: str
    status: str  # "pending", "accepted", "declined"
    created_at: datetime
    responded_at: Optional[datetime] = None


class UserPublicProfile(BaseModel):
    """Public profile for friend system"""
    id: str
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    total_games: int
    favorite_category: Optional[str] = None
    member_since: datetime 