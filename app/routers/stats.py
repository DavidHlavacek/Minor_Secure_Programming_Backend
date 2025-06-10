from fastapi import APIRouter, Depends, HTTPException, status
from app.models.games import StatsRefreshRequest, MOBAStats, FPSStats, RPGStats
from app.models.stats import StatsResponse, UserProfile, CacheStatus
from app.core.security import get_current_active_user
from app.core.database import get_database
from app.services.stats_service import StatsService


router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/games/{game_id}", response_model=StatsResponse)
async def get_game_stats(
    game_id: str,
    current_user = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Get stats for a specific game.
    Returns cached stats or fetches from external API if needed.
    """
    # TODO: Use StatsService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Get game stats not implemented yet"
    )


@router.post("/games/{game_id}/refresh", response_model=StatsResponse)
async def refresh_game_stats(
    game_id: str,
    refresh_request: StatsRefreshRequest,
    current_user = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Refresh stats from external API for a specific game.
    """
    # TODO: Use StatsService
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh game stats not implemented yet"
    )


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    Get user's gaming profile with stats aggregated by category.
    """
    # TODO: Use StatsService to aggregate stats by category
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User profile aggregation not implemented yet"
    )


@router.get("/categories/{category}/schema")
async def get_category_schema(category: str):
    """
    Get the schema for a specific game category.
    Useful for mobile app to know what fields are available.
    """
    schemas = {
        "MOBA": MOBAStats.schema(),
        "FPS": FPSStats.schema(), 
        "RPG": RPGStats.schema()
    }
    
    if category.upper() not in schemas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category}' not supported"
        )
    
    return {
        "category": category.upper(),
        "schema": schemas[category.upper()]
    }

 