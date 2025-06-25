from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
from app.services.external_apis.riot_api import RiotAPIService
from app.core.database import get_db

# Load environment variables
load_dotenv()

router = APIRouter(tags=["lol"])

@router.get("/summoner/{region}/{summoner_name}")
async def get_summoner_by_name(region: str, summoner_name: str):
    """Get summoner information by summoner name"""
    # Get API key from environment variables
    riot_api_key = os.getenv('RIOT_API_KEY')
    print(f"Using Riot API key: {riot_api_key[:5]}..." if riot_api_key and len(riot_api_key) > 5 else "No valid Riot API key found")
    riot_api = RiotAPIService(api_key=riot_api_key)
    try:
        summoner_data = await riot_api.get_summoner_by_name(summoner_name, region)
        return {
            "success": True,
            "isMockData": "mock_" in str(summoner_data),
            "data": summoner_data
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_summoner_by_name: {e}\n{error_details}")
        return {
            "success": False, 
            "message": f"Error: {str(e)}"
        }

@router.get("/ranked/{region}/{summoner_id}")
async def get_ranked_stats(region: str, summoner_id: str):
    """Get ranked stats for a summoner"""
    # Get API key from environment variables
    riot_api_key = os.getenv('RIOT_API_KEY')
    print(f"Using Riot API key: {riot_api_key[:5]}..." if riot_api_key and len(riot_api_key) > 5 else "No valid Riot API key found")
    riot_api = RiotAPIService(api_key=riot_api_key)
    try:
        ranked_data = await riot_api.get_league_entries(summoner_id, region)
        
        # Find solo queue data
        solo_queue_data = None
        for queue_data in ranked_data:
            if queue_data.get("queueType") == "RANKED_SOLO_5x5":
                solo_queue_data = queue_data
                # Calculate win rate
                wins = solo_queue_data.get("wins", 0)
                losses = solo_queue_data.get("losses", 0)
                total_games = wins + losses
                solo_queue_data["winRate"] = wins / total_games if total_games > 0 else 0
                break
        
        return {
            "success": True,
            "data": solo_queue_data
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@router.get("/mastery/{region}/{summoner_id}")
async def get_champion_mastery(region: str, summoner_id: str, count: int = 3):
    """Get champion mastery data for a summoner"""
    # Get API key from environment variables
    riot_api_key = os.getenv('RIOT_API_KEY')
    print(f"Using Riot API key: {riot_api_key[:5]}..." if riot_api_key and len(riot_api_key) > 5 else "No valid Riot API key found")
    riot_api = RiotAPIService(api_key=riot_api_key)
    try:
        mastery_data = await riot_api.get_champion_mastery(summoner_id, region)
        
        # Limit to requested count and add champion names
        # In a real app, you'd look up champion names from static data
        champion_names = {
            157: "Yasuo",
            238: "Zed", 
            103: "Ahri",
            # Add more champion IDs and names as needed
        }
        
        for champion in mastery_data:
            champion_id = champion.get("championId", 0)
            champion["championName"] = champion_names.get(champion_id, f"Champion {champion_id}")
        
        return {
            "success": True,
            "data": mastery_data[:count]
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@router.get("/matches/{region}/{puuid}")
async def get_recent_matches(region: str, puuid: str, count: int = 5):
    """Get recent matches for a summoner"""
    # Get API key from environment variables
    riot_api_key = os.getenv('RIOT_API_KEY')
    print(f"Using Riot API key: {riot_api_key[:5]}..." if riot_api_key and len(riot_api_key) > 5 else "No valid Riot API key found")
    riot_api = RiotAPIService(api_key=riot_api_key)
    try:
        # First get match IDs
        match_ids = await riot_api.get_match_ids_by_puuid(puuid, region, count)
        
        # Then get match details for each ID
        matches = []
        for match_id in match_ids:
            match_data = await riot_api.get_match_by_id(match_id, region)
            
            # Find the participant data for the requested puuid
            for participant in match_data.get("participants", []):
                if participant.get("puuid") == puuid:
                    summary = {
                        "gameId": match_data.get("gameId", match_id),
                        "queueType": match_data.get("queueType", "Unknown"),
                        "gameCreation": match_data.get("gameCreation", 0),
                        "gameDuration": match_data.get("gameDuration", 0),
                        "win": participant.get("win", False),
                        "kills": participant.get("kills", 0),
                        "deaths": participant.get("deaths", 0),
                        "assists": participant.get("assists", 0),
                        "championId": participant.get("championId", 0),
                        "championName": participant.get("championName", f"Champion {participant.get('championId', 0)}"),
                    }
                    
                    # Calculate KDA
                    deaths = summary["deaths"]
                    summary["kda"] = (summary["kills"] + summary["assists"]) / max(deaths, 1)
                    
                    matches.append(summary)
                    break
        
        return {
            "success": True,
            "data": matches
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@router.get("/profile/{region}/{summoner_name}")
async def get_complete_profile(region: str, summoner_name: str):
    """Get complete profile data including summoner info, ranked stats, and more"""
    # Get API key from environment variables
    riot_api_key = os.getenv('RIOT_API_KEY')
    print(f"Using Riot API key: {riot_api_key[:5]}..." if riot_api_key and len(riot_api_key) > 5 else "No valid Riot API key found")
    riot_api = RiotAPIService(api_key=riot_api_key)
    try:
        # 1. Get summoner data
        summoner_data = await riot_api.get_summoner_by_name(summoner_name, region)
        
        # 2. Get ranked data
        ranked_data = await get_ranked_stats(region, summoner_data.get("id", ""))
        ranked_stats = ranked_data.get("data")
        
        # 3. Get champion mastery data
        mastery_data = await get_champion_mastery(region, summoner_data.get("id", ""), 3)
        top_champions = mastery_data.get("data", [])
        
        # 4. Get recent matches
        matches_data = await get_recent_matches(region, summoner_data.get("puuid", ""), 5)
        recent_matches = matches_data.get("data", [])
        
        # 5. Compile complete profile
        complete_profile = {
            "summonerInfo": summoner_data,
            "rankedStats": ranked_stats,
            "topChampions": top_champions,
            "recentMatches": recent_matches
        }
        
        # 6. Save to database for caching purposes
        db = await get_database_client()
        await db.upsert("lol_profiles", {"puuid": summoner_data.get("puuid")}, {
            "puuid": summoner_data.get("puuid"),
            "profile_data": complete_profile,
            "last_updated": "NOW()"
        })
        
        return {
            "success": True,
            "data": complete_profile
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
