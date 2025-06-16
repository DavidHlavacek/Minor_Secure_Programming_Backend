from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.services.external_apis.overwatch_api import OverFastAPIService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

async def get_overwatch_service() -> OverFastAPIService:
    """Dependency to get the OverFastAPIService instance."""
    return OverFastAPIService()

@router.get("/players/{battletag}", response_model=Dict[str, Any])
async def get_player_profile(
    battletag: str,
    overwatch_service: OverFastAPIService = Depends(get_overwatch_service)
):
    """
    Get Overwatch 2 player profile information.
    
    Args:
        battletag: Player's battletag (format: name-1234)
    """
    try:
        data = await overwatch_service.get_player_profile(battletag)
        # Check if the response contains an error message
        if isinstance(data, dict) and data.get('error'):
            return {"success": True, "data": {"player_name": "unknown", "player_level": 0, "endorsement_level": 0}}
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error fetching player profile: {str(e)}")
        if "Player not found" in str(e) or "404" in str(e):
            # Return a default profile structure instead of raising an exception
            return {"success": True, "data": {"player_name": "unknown", "player_level": 0, "endorsement_level": 0}}
        # For other exceptions, return a similar structure but with error info
        return {"success": True, "data": {"player_name": "unknown", "player_level": 0, "endorsement_level": 0, "error": "Profile unavailable"}}

@router.get("/players/{battletag}/summary", response_model=Dict[str, Any])
async def get_player_summary(
    battletag: str,
    overwatch_service: OverFastAPIService = Depends(get_overwatch_service)
):
    """
    Get Overwatch 2 player summary statistics.
    
    Args:
        battletag: Player's battletag (format: name-1234)
    """
    try:
        data = await overwatch_service.get_player_summary(battletag)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error fetching player summary: {str(e)}")
        if "Player not found" in str(e):
            raise HTTPException(status_code=404, detail="Player not found or profile is private")
        raise HTTPException(status_code=500, detail=f"Error fetching player data: {str(e)}")

@router.get("/players/{battletag}/competitive", response_model=Dict[str, Any])
async def get_player_competitive(
    battletag: str,
    overwatch_service: OverFastAPIService = Depends(get_overwatch_service)
):
    """
    Get Overwatch 2 player competitive rankings.
    
    Args:
        battletag: Player's battletag (format: name-1234)
    """
    try:
        data = await overwatch_service.get_player_competitive(battletag)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error fetching player competitive rankings: {str(e)}")
        if "Player not found" in str(e):
            raise HTTPException(status_code=404, detail="Player not found or profile is private")
        raise HTTPException(status_code=500, detail=f"Error fetching player data: {str(e)}")

@router.get("/players/{battletag}/heroes/{mode}", response_model=Dict[str, Any])
async def get_player_heroes(
    battletag: str,
    mode: str,
    overwatch_service: OverFastAPIService = Depends(get_overwatch_service)
):
    """
    Get Overwatch 2 player statistics by hero.
    
    Args:
        battletag: Player's battletag (format: name-1234)
        mode: Either 'quickplay' or 'competitive'
    """
    if mode not in ["quickplay", "competitive"]:
        raise HTTPException(status_code=400, detail="Mode must be either 'quickplay' or 'competitive'")
    
    try:
        data = await overwatch_service.get_player_heroes(battletag, mode)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error fetching player heroes: {str(e)}")
        if "Player not found" in str(e):
            raise HTTPException(status_code=404, detail="Player not found or profile is private")
        raise HTTPException(status_code=500, detail=f"Error fetching player data: {str(e)}")

@router.get("/heroes", response_model=Dict[str, Any])
async def get_heroes(
    overwatch_service: OverFastAPIService = Depends(get_overwatch_service)
):
    """Get information about all Overwatch 2 heroes."""
    try:
        data = await overwatch_service.get_heroes()
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error fetching heroes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching heroes data: {str(e)}")

@router.get("/heroes/{hero_key}", response_model=Dict[str, Any])
async def get_hero_details(
    hero_key: str,
    overwatch_service: OverFastAPIService = Depends(get_overwatch_service)
):
    """
    Get detailed information about a specific Overwatch 2 hero.
    
    Args:
        hero_key: Hero key (e.g., 'ana', 'soldier-76', etc.)
    """
    try:
        data = await overwatch_service.get_hero_details(hero_key)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error fetching hero details: {str(e)}")
        if "404" in str(e):
            raise HTTPException(status_code=404, detail="Hero not found")
        raise HTTPException(status_code=500, detail=f"Error fetching hero data: {str(e)}")

@router.get("/maps", response_model=Dict[str, Any])
async def get_maps(
    overwatch_service: OverFastAPIService = Depends(get_overwatch_service)
):
    """Get information about all Overwatch 2 maps."""
    try:
        data = await overwatch_service.get_maps()
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error fetching maps: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching maps data: {str(e)}")

@router.get("/profile/{battletag}", response_model=Dict[str, Any])
async def get_combined_player_profile(
    battletag: str,
    overwatch_service: OverFastAPIService = Depends(get_overwatch_service)
):
    """
    Get combined player profile with summary stats and competitive rankings.
    
    Args:
        battletag: Player's battletag (format: name-1234)
    """
    try:
        data = await overwatch_service.get_combined_player_profile(battletag)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error fetching combined player profile: {str(e)}")
        if "Player not found" in str(e):
            raise HTTPException(status_code=404, detail="Player not found or profile is private")
        raise HTTPException(status_code=500, detail=f"Error fetching player data: {str(e)}")
