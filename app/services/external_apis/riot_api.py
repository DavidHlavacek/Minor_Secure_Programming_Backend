"""
Riot API Service

Integration with Riot Games API for League of Legends and Valorant statistics.
"""

from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime


class RiotAPIService:
    """
    Service for Riot Games API integration.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://na1.api.riotgames.com"
        self.rate_limits = {
            "personal": 100,  # requests per 2 minutes
            "development": 100,
            "production": 3000
        }
    
    async def get_summoner_by_name(self, summoner_name: str, region: str = "na1") -> Dict[str, Any]:
        """
        Get summoner information by name.
        
        Args:
            summoner_name: The summoner name to look up
            region: The region to query (e.g., na1, euw1)
            
        Returns:
            Dict with summoner information
            
        Raises:
            HTTPException: If the API request fails
        """
        # Validate region
        if region not in self.get_supported_regions():
            raise ValueError(f"Invalid region: {region}")
        
        # URL encode the summoner name
        from urllib.parse import quote
        encoded_name = quote(summoner_name)
        
        # Build the request URL
        url = self._build_url(f"/lol/summoner/v4/summoners/by-name/{encoded_name}", region)
        
        try:
            # Make the API request
            response = await self._make_request(url)
            return response
        except Exception as e:
            # For demo purposes, return mocked data if API key isn't set up
            if not self.api_key:
                return {
                    "id": f"mock_summoner_id_{summoner_name}",
                    "accountId": f"mock_account_id_{summoner_name}",
                    "puuid": f"mock_puuid_{summoner_name}",
                    "name": summoner_name,
                    "profileIconId": 4568,
                    "revisionDate": int(datetime.now().timestamp() * 1000),
                    "summonerLevel": 145
                }
            raise e
    
    async def get_ranked_stats(self, summoner_id: str, region: str = "na1") -> Dict[str, Any]:
        """
        Get ranked statistics for a summoner.
        
        Args:
            summoner_id: The encrypted summoner ID to look up
            region: The region to query (e.g., na1, euw1)
            
        Returns:
            Dict with ranked statistics
        """
        # Validate region
        if region not in self.get_supported_regions():
            raise ValueError(f"Invalid region: {region}")
            
        # Build the request URL
        url = self._build_url(f"/lol/league/v4/entries/by-summoner/{summoner_id}", region)
        
        try:
            # Make the API request - this returns a list of queue entries
            entries = await self._make_request(url)
            
            # Find the solo queue entry
            solo_queue = next((entry for entry in entries if entry.get("queueType") == "RANKED_SOLO_5x5"), None)
            
            if solo_queue:
                return solo_queue
            
            # If no solo queue data, return default
            return {
                "queueType": "RANKED_SOLO_5x5",
                "tier": "UNRANKED",
                "rank": "",
                "summonerId": summoner_id,
                "wins": 0,
                "losses": 0,
                "leaguePoints": 0
            }
            
        except Exception as e:
            # For demo purposes, return mocked data if API key isn't set up
            if not self.api_key:
                return {
                    "queueType": "RANKED_SOLO_5x5",
                    "tier": "GOLD", 
                    "rank": "II",
                    "summonerId": summoner_id,
                    "wins": 67,
                    "losses": 53,
                    "leaguePoints": 42,
                    "veteran": False,
                    "inactive": False,
                    "freshBlood": False,
                    "hotStreak": True
                }
            raise e
    
    async def get_champion_mastery(self, summoner_id: str, region: str = "na1", limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get champion mastery data for a summoner.
        
        Args:
            summoner_id: The encrypted summoner ID to look up
            region: The region to query (e.g., na1, euw1)
            limit: Number of top champions to return (default 5)
            
        Returns:
            List of champion mastery entries
        """
        # Validate region
        if region not in self.get_supported_regions():
            raise ValueError(f"Invalid region: {region}")
            
        # Build the request URL for getting all champion masteries
        url = self._build_url(f"/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}", region)
        
        try:
            # Make the API request
            mastery_data = await self._make_request(url)
            
            # Return the top champions by mastery points
            return mastery_data[:limit] if mastery_data else []
            
        except Exception as e:
            # For demo purposes, return mocked data if API key isn't set up
            if not self.api_key:
                # Mock data for top 3 champions
                return [
                    {
                        "championId": 157,  # Yasuo
                        "championLevel": 7,
                        "championPoints": 234567,
                        "lastPlayTime": int(datetime.now().timestamp() * 1000),
                        "championPointsSinceLastLevel": 0,
                        "championPointsUntilNextLevel": 0,
                        "chestGranted": True,
                        "tokensEarned": 0
                    },
                    {
                        "championId": 99,  # Lux
                        "championLevel": 6,
                        "championPoints": 105680,
                        "lastPlayTime": int(datetime.now().timestamp() * 1000) - 86400000,  # 1 day ago
                        "championPointsSinceLastLevel": 1500,
                        "championPointsUntilNextLevel": 0,
                        "chestGranted": False,
                        "tokensEarned": 2
                    },
                    {
                        "championId": 412,  # Thresh
                        "championLevel": 5,
                        "championPoints": 87420,
                        "lastPlayTime": int(datetime.now().timestamp() * 1000) - 172800000,  # 2 days ago
                        "championPointsSinceLastLevel": 0,
                        "championPointsUntilNextLevel": 12580,
                        "chestGranted": True,
                        "tokensEarned": 0
                    }
                ]
            raise e
    
    async def get_match_history(
        self, 
        puuid: str, 
        region: str = "americas",
        count: int = 10
    ) -> List[str]:
        """
        Get recent match IDs for a player.
        
        Args:
            puuid: The encrypted PUUID of the player
            region: The routing region (e.g., americas, europe)
            count: Number of matches to retrieve (default 10)
            
        Returns:
            List of match IDs
        """
        # Validate region - note that match history uses routing regions
        routing_regions = ["americas", "europe", "asia"]
        if region not in routing_regions:
            raise ValueError(f"Invalid routing region: {region}. Must be one of {routing_regions}")
            
        # Build the request URL
        url = self._build_url(f"/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}", region)
        
        try:
            # Make the API request
            match_ids = await self._make_request(url)
            return match_ids
            
        except Exception as e:
            # For demo purposes, return mocked data if API key isn't set up
            if not self.api_key:
                # Generate random match IDs for demonstration
                import random
                return [
                    f"NA1_{random.randint(4000000000, 4999999999)}"
                    for _ in range(count)
                ]
            raise e
    
    async def get_match_details(self, match_id: str, region: str = "americas") -> Dict[str, Any]:
        """
        Get detailed match information.
        
        Args:
            match_id: The match ID to retrieve details for
            region: The routing region (e.g., americas, europe)
            
        Returns:
            Dict with match details
        """
        # Validate region - note that match details uses routing regions
        routing_regions = ["americas", "europe", "asia"]
        if region not in routing_regions:
            raise ValueError(f"Invalid routing region: {region}. Must be one of {routing_regions}")
            
        # Build the request URL
        url = self._build_url(f"/lol/match/v5/matches/{match_id}", region)
        
        try:
            # Make the API request
            match_data = await self._make_request(url)
            return match_data
            
        except Exception as e:
            # For demo purposes, return mocked data if API key isn't set up
            if not self.api_key:
                import random
                from datetime import datetime, timedelta
                
                # Create a mock match that happened recently
                now = datetime.now()
                game_creation = int((now - timedelta(hours=random.randint(1, 48))).timestamp() * 1000)
                game_duration = random.randint(15*60, 45*60)  # 15-45 minutes in seconds
                
                # Mock participant data (just a simplified version)
                participants = []
                for i in range(10):  # 5v5 game
                    team_id = 100 if i < 5 else 200  # Blue/Red side
                    win = team_id == 100  # Let blue side win for mocked data
                    
                    # Random stats for the participant
                    kills = random.randint(0, 15)
                    deaths = random.randint(0, 12)
                    assists = random.randint(0, 20)
                    
                    participants.append({
                        "participantId": i + 1,
                        "teamId": team_id,
                        "championId": random.randint(1, 160),  # Random champion ID
                        "win": win,
                        "kills": kills,
                        "deaths": deaths,
                        "assists": assists,
                        "totalDamageDealt": random.randint(10000, 50000),
                        "goldEarned": random.randint(8000, 20000),
                        "champLevel": random.randint(13, 18),
                        "totalMinionsKilled": random.randint(50, 300),
                        "item0": random.randint(1000, 4000),
                        "item1": random.randint(1000, 4000),
                        "item2": random.randint(1000, 4000),
                        "item3": random.randint(1000, 4000),
                        "item4": random.randint(1000, 4000),
                        "item5": random.randint(1000, 4000),
                        "item6": random.randint(1000, 4000),
                        "summonerName": f"Player{i+1}",
                        "role": random.choice(["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "SUPPORT"])
                    })
                
                return {
                    "metadata": {
                        "matchId": match_id,
                        "participants": [f"Player{i+1}" for i in range(10)]
                    },
                    "info": {
                        "gameCreation": game_creation,
                        "gameDuration": game_duration,
                        "gameMode": "CLASSIC",
                        "gameType": "MATCHED_GAME",
                        "gameVersion": "13.10.1",  # Example game version
                        "mapId": 11,  # Summoner's Rift
                        "participants": participants,
                        "teams": [
                            {
                                "teamId": 100,
                                "win": True,
                                "baronKills": random.randint(0, 2),
                                "dragonKills": random.randint(0, 4),
                                "towerKills": random.randint(5, 11)
                            },
                            {
                                "teamId": 200,
                                "win": False,
                                "baronKills": random.randint(0, 1),
                                "dragonKills": random.randint(0, 3),
                                "towerKills": random.randint(0, 5)
                            }
                        ]
                    }
                }
            raise e
    
    async def validate_api_key(self) -> bool:
        """
        Validate the API key by making a test request.
        
        Returns:
            True if API key is valid, False otherwise
        """
        import logging
        logger = logging.getLogger("riot_api")
        
        if not self.api_key:
            logger.warning("No API key provided")
            return False
            
        try:
            # Make a simple API call that should work with any valid key
            url = self._build_url("/lol/status/v4/platform-data", "na1")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self._get_headers(), timeout=5.0)
                
                if response.status_code == 200:
                    logger.info("API key validated successfully")
                    return True
                elif response.status_code == 403 or response.status_code == 401:
                    logger.error("API key is invalid")
                    return False
                else:
                    logger.warning(f"Unexpected status code during validation: {response.status_code}")
                    # If we get a different error (like rate limiting), assume the key might be valid
                    return True
                    
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            # If there's an error, assume the key might be invalid
            return False
    
    def _build_url(self, endpoint: str, region: str = "na1") -> str:
        """
        Build full API URL for endpoint.
        """
        base_urls = {
            "na1": "https://na1.api.riotgames.com",
            "euw1": "https://euw1.api.riotgames.com",
            "kr": "https://kr.api.riotgames.com",
            "americas": "https://americas.api.riotgames.com",
            "europe": "https://europe.api.riotgames.com",
            "asia": "https://asia.api.riotgames.com"
        }
        
        base_url = base_urls.get(region, self.base_url)
        return f"{base_url}{endpoint}"
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers with API key.
        """
        return {
            "X-Riot-Token": self.api_key or "",
            "Accept": "application/json",
            "User-Agent": "MinorSecureProgramming/1.0"
        }
    
    async def _make_request(self, url: str) -> Dict[str, Any]:
        """
        Make HTTP request to Riot API with error handling.
        
        Args:
            url: The URL to request
            
        Returns:
            Response data as dict
            
        Raises:
            Various exceptions for API errors
        """
        from fastapi import HTTPException, status
        import logging
        
        # Set up logging
        logger = logging.getLogger("riot_api")
        
        # Log the request (without API key)
        logger.info(f"Making request to: {url}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self._get_headers(), timeout=10.0)
                
                # Debug response
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response headers: {response.headers}")
                try:
                    logger.info(f"Response body: {response.text}")
                except:
                    logger.info("Could not log response body")
                    
                # Handle common API errors
                if response.status_code == 429:
                    logger.warning(f"Rate limit exceeded: {response.headers}")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again later."
                    )
                    
                elif response.status_code == 403:
                    logger.error("API key invalid or unauthorized")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="API key is invalid or unauthorized"
                    )
                    
                elif response.status_code == 404:
                    logger.warning(f"Resource not found: {url}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Resource not found (e.g., summoner doesn't exist)"
                    )
                
                # Raise for other status codes
                response.raise_for_status()
                
                # Return the JSON response
                return response.json()
                
        except httpx.TimeoutException:
            logger.error(f"Request timed out: {url}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request to Riot API timed out"
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            # We already handled the common cases above
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error from Riot API: {str(e)}"
            )
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}"
            )
    
    @staticmethod
    def get_supported_regions() -> List[str]:
        """
        Get list of supported regions.
        """
        return ["na1", "euw1", "kr", "br1", "jp1", "ru", "oc1", "tr1", "la1", "la2"]
    
    @staticmethod
    def get_queue_types() -> List[Dict[str, Any]]:
        """
        Get list of supported queue types.
        """
        return [
            {"id": "RANKED_SOLO_5x5", "name": "Ranked Solo/Duo", "description": "5v5 Ranked Solo games"},
            {"id": "RANKED_FLEX_SR", "name": "Ranked Flex", "description": "5v5 Ranked Flex games"},
            {"id": "RANKED_TFT_PAIRS", "name": "TFT Pairs", "description": "Teamfight Tactics Pairs"}
        ] 