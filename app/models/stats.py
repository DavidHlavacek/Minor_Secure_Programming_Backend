from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# Simple Stats Models
class StatsResponse(BaseModel):
    """Basic stats response for any game"""
    game_id: str
    user_id: str
    category: str
    stats_data: Dict[str, Any]  # Category-standardized stats
    last_updated: datetime
    source: str = "external_api"  # external_api, manual, cached


class ProfileStats(BaseModel):
    """Aggregated stats for user profile"""
    category: str
    total_games: int
    
    # Basic aggregated metrics
    total_wins: Optional[int] = None
    total_losses: Optional[int] = None
    win_rate: Optional[float] = None
    
    # Best game in this category
    best_game: Optional[str] = None
    highest_rank: Optional[str] = None
    
    last_updated: Optional[datetime] = None


class UserProfile(BaseModel):
    """User's gaming profile with category breakdown"""
    user_id: str
    username: str
    total_games: int
    categories: List[ProfileStats]
    last_activity: Optional[datetime] = None


# Simple Cache Info
class CacheStatus(BaseModel):
    """Simple cache status for a game"""
    game_id: str
    is_cached: bool
    last_updated: Optional[datetime] = None
    cache_expires_at: Optional[datetime] = None 