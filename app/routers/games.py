from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.models.games import (
    GameCreate, GameUpdate, GameResponse, GamesListResponse, GameFilter
)
from app.core.security import get_current_active_user
from app.core.database import get_db
from app.services.games_service import GamesService


router = APIRouter(prefix="/games", tags=["games"])


@router.post("/", response_model=GameResponse)
async def create_game(
    game_data: GameCreate,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """
    Add a new game to user's library.
    
    Flow:
    1. Validate game data
    2. Check for duplicates
    3. Save to database
    4. Return created game
    """
    # TODO: Use GamesService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Game creation not implemented yet"
    )


@router.get("/", response_model=GamesListResponse)
async def get_user_games(
    category: Optional[str] = Query(None, description="Filter by game category"),
    search: Optional[str] = Query(None, description="Search games by name"),
    limit: int = Query(20, ge=1, le=100, description="Number of games to return"),
    offset: int = Query(0, ge=0, description="Number of games to skip"),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """
    Get user's games with optional filtering and pagination.
    
    Flow:
    1. Filter by category if provided
    2. Search by name if provided
    3. Apply pagination
    4. Return games list
    """
    # TODO: Use GamesService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get games not implemented yet"
    )


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: str,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """
    Get specific game by ID.
    
    Flow:
    1. Verify game belongs to user
    2. Return game details
    """
    # TODO: Use GamesService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get game not implemented yet"
    )


@router.put("/{game_id}", response_model=GameResponse)
async def update_game(
    game_id: str,
    game_data: GameUpdate,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """
    Update game information.
    
    Flow:
    1. Verify game belongs to user
    2. Update game data
    3. Return updated game
    """
    # TODO: Use GamesService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Game update not implemented yet"
    )


@router.delete("/{game_id}")
async def delete_game(
    game_id: str,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """
    Remove game from user's library.
    
    Flow:
    1. Verify game belongs to user
    2. Delete game and associated stats
    3. Return success message
    """
    # TODO: Use GamesService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Game deletion not implemented yet"
    )


@router.get("/categories")
async def get_game_categories():
    """
    Get available game categories for game creation.
    """
    return {
        "categories": [
            {"name": "MOBA", "supports_stats": True},
            {"name": "FPS", "supports_stats": True},
            {"name": "RPG", "supports_stats": True},
            {"name": "Strategy", "supports_stats": False},
            {"name": "Sports", "supports_stats": False}
        ]
    } 