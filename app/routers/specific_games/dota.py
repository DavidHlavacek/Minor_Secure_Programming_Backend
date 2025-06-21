"""
OpenDota API Endpoints

Endpoints for accessing Dota 2 statistics via OpenDota API
No API key required for most endpoints!
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status, Security
from typing import Dict, List, Optional, Any, Union

from app.services.external_apis.open_dota import OpenDotaService
from app.middleware.auth_middleware import get_current_user, get_optional_user

router = APIRouter(tags=["dota"])

# Example pro player IDs for testing
PRO_PLAYERS = {
    "arteezy": "86745912",     # Arteezy
    "Nisha (smurf 2)": "201358612",
    "sumail": "111620041",     # SumaiL
    "notail": "19672354",      # N0tail
    "puppey": "87278757"       # Puppey
}

@router.get("/players/{account_id}")
async def get_player_info(account_id: str, current_user: Dict = Security(get_current_user)):
    """Get player information by Steam ID"""
    open_dota = OpenDotaService()
    try:
        # Handle pro player nicknames
        if account_id.lower() in PRO_PLAYERS:
            account_id = PRO_PLAYERS[account_id.lower()]
            
        player_data = await open_dota.get_player_info(account_id)
        return {
            "success": True,
            "data": player_data
        }
    except Exception as e:
        print(f"Error getting player info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get player info: {str(e)}"
        )

@router.get("/players/{account_id}/recent-matches")
async def get_recent_matches(account_id: str, limit: int = 10, current_user: Dict = Security(get_current_user)):
    """Get recent matches for a player"""
    open_dota = OpenDotaService()
    try:
        # Handle pro player nicknames
        if account_id.lower() in PRO_PLAYERS:
            account_id = PRO_PLAYERS[account_id.lower()]
            
        matches = await open_dota.get_player_recent_matches(account_id, limit)
        return {
            "success": True,
            "data": matches
        }
    except Exception as e:
        print(f"Error getting recent matches: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent matches: {str(e)}"
        )

@router.get("/players/{account_id}/win-loss")
async def get_win_loss(account_id: str, current_user: Dict = Security(get_current_user)):
    """Get player win/loss record"""
    open_dota = OpenDotaService()
    try:
        # Handle pro player nicknames
        if account_id.lower() in PRO_PLAYERS:
            account_id = PRO_PLAYERS[account_id.lower()]
            
        wl_data = await open_dota.get_player_win_loss(account_id)
        return {
            "success": True,
            "data": wl_data
        }
    except Exception as e:
        print(f"Error getting win/loss: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get win/loss: {str(e)}"
        )

@router.get("/players/{account_id}/heroes")
async def get_player_heroes(account_id: str, current_user: Dict = Security(get_current_user)):
    """Get player hero statistics"""
    open_dota = OpenDotaService()
    try:
        # Handle pro player nicknames
        if account_id.lower() in PRO_PLAYERS:
            account_id = PRO_PLAYERS[account_id.lower()]
            
        heroes = await open_dota.get_player_heroes(account_id)
        return {
            "success": True,
            "data": heroes
        }
    except Exception as e:
        print(f"Error getting player heroes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get player heroes: {str(e)}"
        )

@router.get("/heroes")
async def get_heroes(current_user: Dict = Depends(get_optional_user)):
    """Get list of all heroes"""
    open_dota = OpenDotaService()
    try:
        heroes = await open_dota.get_heroes()
        return {
            "success": True,
            "data": heroes
        }
    except Exception as e:
        print(f"Error getting heroes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get heroes: {str(e)}"
        )

@router.get("/hero-stats")
async def get_hero_stats(current_user: Dict = Depends(get_optional_user)):
    """Get stats for all heroes"""
    open_dota = OpenDotaService()
    try:
        hero_stats = await open_dota.get_hero_stats()
        return {
            "success": True,
            "data": hero_stats
        }
    except Exception as e:
        print(f"Error getting hero stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hero stats: {str(e)}"
        )

@router.get("/matches/{match_id}")
async def get_match_details(match_id: str, current_user: Dict = Security(get_current_user)):
    """Get detailed information about a match"""
    open_dota = OpenDotaService()
    try:
        match_data = await open_dota.get_match_details(match_id)
        return {
            "success": True,
            "data": match_data
        }
    except Exception as e:
        print(f"Error getting match details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match details: {str(e)}"
        )

@router.get("/public-matches")
async def get_public_matches(limit: int = 10, current_user: Dict = Depends(get_optional_user)):
    """Get list of recent public matches"""
    open_dota = OpenDotaService()
    try:
        matches = await open_dota.get_public_matches(limit)
        return {
            "success": True,
            "data": matches
        }
    except Exception as e:
        print(f"Error getting public matches: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get public matches: {str(e)}"
        )

@router.get("/pro-players")
async def get_pro_players(current_user: Dict = Depends(get_optional_user)):
    """Get list of professional players"""
    open_dota = OpenDotaService()
    try:
        players = await open_dota.get_pro_players()
        return {
            "success": True,
            "data": players
        }
    except Exception as e:
        print(f"Error getting pro players: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pro players: {str(e)}"
        )

@router.get("/pro-matches")
async def get_pro_matches(limit: int = 10, current_user: Dict = Depends(get_optional_user)):
    """Get list of professional matches"""
    open_dota = OpenDotaService()
    try:
        matches = await open_dota.get_pro_matches(limit)
        return {
            "success": True,
            "data": matches
        }
    except Exception as e:
        print(f"Error getting pro matches: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pro matches: {str(e)}"
        )

@router.get("/profile/{account_id}")
async def get_player_profile(account_id: str, current_user: Dict = Security(get_current_user)):
    """Get complete player profile with important stats (combined endpoint)"""
    open_dota = OpenDotaService()
    try:
        # Handle pro player nicknames
        if account_id.lower() in PRO_PLAYERS:
            account_id = PRO_PLAYERS[account_id.lower()]
            
        # Get all player data in parallel
        player_info = await open_dota.get_player_info(account_id)
        recent_matches = await open_dota.get_player_recent_matches(account_id, 5)
        win_loss = await open_dota.get_player_win_loss(account_id)
        heroes = await open_dota.get_player_heroes(account_id)
        
        # Filter hero data to top 5
        if heroes and isinstance(heroes, list):
            heroes = sorted(heroes, key=lambda x: x.get('games', 0), reverse=True)[:5]
        
        # Combine into a profile object
        profile = {
            "player": player_info,
            "win_loss": win_loss,
            "recent_matches": recent_matches,
            "top_heroes": heroes
        }
        
        return {
            "success": True,
            "data": profile
        }
    except Exception as e:
        print(f"Error getting player profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get player profile: {str(e)}"
        )
