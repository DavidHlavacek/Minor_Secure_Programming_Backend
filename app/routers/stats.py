from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from app.models.games import StatsRefreshRequest, MOBAStats, FPSStats, RPGStats
from app.models.stats import StatsResponse, UserProfile, CacheStatus
from app.core.security import get_current_active_user
from app.core.database import get_db
from app.services.stats_service import StatsService
from app.services.external_apis.riot_api import RiotAPIService
from app.services.external_apis.transformer import StatsTransformer

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stats", tags=["statistics"])

# Initialize Riot API service
riot_service = RiotAPIService()


@router.get("/games/{game_id}", response_model=StatsResponse)
async def get_game_stats(
    game_id: str,
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
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
    db = Depends(get_db)
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
    db = Depends(get_db)
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


# League of Legends specific endpoints
@router.get("/lol/summoner/{summoner_name}")
async def get_lol_summoner_info(
    summoner_name: str, 
    region: str = Query("na1", description="Riot region code"),
    current_user = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get basic summoner information for a League of Legends player.
    
    Args:
        summoner_name: The summoner name to look up
        region: The Riot region code (e.g., na1, euw1)
        
    Returns:
        Dict with summoner information
    """
    try:
        logger.info(f"Fetching summoner info for {summoner_name} in {region}")
        summoner_data = await riot_service.get_summoner_by_name(summoner_name, region)
        return {
            "status": "success",
            "data": summoner_data,
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        # Handle invalid region
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching summoner data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve summoner data: {str(e)}"
        )


@router.get("/lol/stats/{summoner_name}")
async def get_lol_stats(
    summoner_name: str, 
    region: str = Query("na1", description="Riot region code"),
    match_count: int = Query(5, description="Number of matches to analyze", ge=1, le=20),
    current_user = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get comprehensive League of Legends stats for a player.
    This endpoint aggregates data from multiple Riot API endpoints.
    
    Args:
        summoner_name: The summoner name to look up
        region: The Riot region code (e.g., na1, euw1)
        match_count: Number of recent matches to analyze
        
    Returns:
        Dict with transformed stats in MOBAStats format
    """
    try:
        # Step 1: Get basic summoner data
        summoner_data = await riot_service.get_summoner_by_name(summoner_name, region)
        
        # Step 2: Get ranked stats using summoner ID
        summoner_id = summoner_data.get("id")
        ranked_data = await riot_service.get_ranked_stats(summoner_id, region)
        
        # Step 3: Get champion mastery data
        mastery_data = await riot_service.get_champion_mastery(summoner_id, region)
        
        # Step 4: Get match history using PUUID
        puuid = summoner_data.get("puuid")
        # Note: Match history uses a different region format (routing value)
        routing_region = "americas" if region in ["na1", "br1", "la1", "la2"] else "europe" if region in ["euw1", "eun1", "tr1", "ru"] else "asia"
        match_ids = await riot_service.get_match_history(puuid, routing_region, match_count)
        
        # Step 5: Fetch details for each match
        match_details = []
        for match_id in match_ids[:5]:  # Limit to avoid excessive API calls
            match_data = await riot_service.get_match_details(match_id, routing_region)
            
            # Find the participant info for our summoner
            participant = None
            if "info" in match_data and "participants" in match_data["info"]:
                for p in match_data["info"]["participants"]:
                    if p.get("puuid") == puuid:
                        participant = p
                        break
            
            if participant:
                match_details.append({"participant": participant})
        
        # Step 6: Transform the combined data to our standard format
        combined_data = {
            "summoner": summoner_data,
            "ranked": ranked_data,
            "mastery": mastery_data,
            "matches": match_details
        }
        
        # Transform to our standardized MOBAStats model
        transformed_stats = StatsTransformer.transform_riot_lol_to_moba(combined_data)
        
        return {
            "status": "success",
            "data": transformed_stats.dict(),
            "raw_data": combined_data if "debug" in region.lower() else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except ValueError as e:
        # Handle invalid parameters
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions from lower layers
        raise
    except Exception as e:
        logger.error(f"Error processing LoL stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve complete LoL stats: {str(e)}"
        )


@router.get("/lol/match/{match_id}")
async def get_lol_match_details(
    match_id: str,
    region: str = Query("americas", description="Riot routing region"),
    current_user = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific League of Legends match.
    
    Args:
        match_id: The match ID to retrieve
        region: The Riot routing region (americas, europe, asia)
        
    Returns:
        Dict with match details
    """
    try:
        match_data = await riot_service.get_match_details(match_id, region)
        return {
            "status": "success",
            "data": match_data,
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching match data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve match data: {str(e)}"
        )