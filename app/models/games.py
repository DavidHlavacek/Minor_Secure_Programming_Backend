from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# TODO: Game Request Models
class GameCreate(BaseModel):
    """
    Game creation request model.
    TODO: Add validation for game data based on Android app requirements
    """
    name: str
    category: str
    username: str  # In-game username


class GameUpdate(BaseModel):
    """
    Game update request model.
    TODO: Allow partial updates of game information
    """
    name: Optional[str] = None
    category: Optional[str] = None
    username: Optional[str] = None


class GameFilter(BaseModel):
    """
    Game filtering request model.
    TODO: Implement filtering options for games list
    """
    category: Optional[str] = None
    search_term: Optional[str] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0


# TODO: Game Response Models
class GameResponse(BaseModel):
    """
    Game response model.
    TODO: Match structure with Android app GameInfo class
    """
    id: str
    user_id: str
    name: str
    category: str
    username: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class GamesListResponse(BaseModel):
    """
    Games list response model.
    TODO: Add pagination support
    """
    games: List[GameResponse]
    total: int
    page: Optional[int] = None
    per_page: Optional[int] = None


# Simple Stats Request
class StatsRefreshRequest(BaseModel):
    """Request to refresh game stats from external API"""
    force_refresh: bool = False


# TODO: Category-Standardized Stats Schemas
class MOBAStats(BaseModel):
    """
    Standardized MOBA category stats (LoL, Dota 2, etc.)
    All MOBA games transform their APIs to this schema.
    """
    player_level: Optional[int] = None
    current_rank: Optional[str] = None
    rank_tier: Optional[str] = None  # Bronze, Silver, Gold, etc.
    rank_division: Optional[str] = None  # I, II, III, IV
    wins: Optional[int] = None
    losses: Optional[int] = None
    win_rate: Optional[float] = None
    main_role: Optional[str] = None
    favorite_champions: Optional[List[str]] = None
    total_games: Optional[int] = None
    average_kda: Optional[float] = None


class FPSStats(BaseModel):
    """
    Standardized FPS category stats (R6, Valorant, CS:GO, etc.)
    All FPS games transform their APIs to this schema.
    """
    player_level: Optional[int] = None
    current_rank: Optional[str] = None
    rank_mmr: Optional[int] = None
    kills: Optional[int] = None
    deaths: Optional[int] = None
    assists: Optional[int] = None
    kd_ratio: Optional[float] = None
    headshot_percentage: Optional[float] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    total_matches: Optional[int] = None
    favorite_operators: Optional[List[str]] = None  # R6 specific but generic enough


class RPGStats(BaseModel):
    """
    Standardized RPG category stats (WoW, FFXIV, etc.)
    """
    character_level: Optional[int] = None
    character_class: Optional[str] = None
    guild_name: Optional[str] = None
    achievements_count: Optional[int] = None
    total_playtime_hours: Optional[float] = None
    equipment_score: Optional[int] = None


# Simple API Response  
class APIResponse(BaseModel):
    """Simple response from external API"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# TODO: Category Models
class GameCategory(BaseModel):
    """
    Game category model.
    TODO: Define available game categories
    """
    name: str
    description: Optional[str] = None
    supported_stats: bool = False  # Whether this category supports stats tracking 