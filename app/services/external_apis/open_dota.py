"""
OpenDota API Service

Integration with OpenDota API for Dota 2 statistics.
No API key required for most endpoints!
"""
import httpx
from typing import Dict, List, Optional, Any
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class OpenDotaService:
    """Service for OpenDota API integration."""
    
    def __init__(self):
        """Initialize the OpenDota service."""
        self.base_url = "https://api.opendota.com/api"
    
    async def get_player_info(self, account_id: str) -> Dict[str, Any]:
        """Get player information by Steam ID."""
        url = f"{self.base_url}/players/{account_id}"
        return await self._make_request(url)
    
    async def get_player_recent_matches(self, account_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent matches for a player."""
        url = f"{self.base_url}/players/{account_id}/recentMatches"
        data = await self._make_request(url)
        return data[:limit] if limit and isinstance(data, list) else data
    
    async def get_player_heroes(self, account_id: str) -> List[Dict[str, Any]]:
        """Get player hero statistics."""
        url = f"{self.base_url}/players/{account_id}/heroes"
        return await self._make_request(url)
    
    async def get_player_win_loss(self, account_id: str) -> Dict[str, int]:
        """Get player win/loss record."""
        url = f"{self.base_url}/players/{account_id}/wl"
        return await self._make_request(url)
    
    async def get_player_rankings(self, account_id: str) -> List[Dict[str, Any]]:
        """Get player hero rankings."""
        url = f"{self.base_url}/players/{account_id}/rankings"
        return await self._make_request(url)
    
    async def get_heroes(self) -> List[Dict[str, Any]]:
        """Get list of all heroes."""
        url = f"{self.base_url}/heroes"
        return await self._make_request(url)
    
    async def get_hero_stats(self) -> List[Dict[str, Any]]:
        """Get stats for all heroes."""
        url = f"{self.base_url}/heroStats"
        return await self._make_request(url)
    
    async def get_match_details(self, match_id: str) -> Dict[str, Any]:
        """Get detailed information about a match."""
        url = f"{self.base_url}/matches/{match_id}"
        return await self._make_request(url)
    
    async def get_public_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of recent public matches."""
        url = f"{self.base_url}/publicMatches?limit={limit}"
        return await self._make_request(url)
    
    async def get_pro_players(self) -> List[Dict[str, Any]]:
        """Get list of professional players."""
        url = f"{self.base_url}/proPlayers"
        return await self._make_request(url)
    
    async def get_pro_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of professional matches."""
        url = f"{self.base_url}/proMatches?limit={limit}"
        return await self._make_request(url)
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the API."""
        url = f"{self.base_url}/metadata"
        return await self._make_request(url)
    
    async def _make_request(self, url: str) -> Any:
        """Make HTTP request to OpenDota API with error handling."""
        try:
            logger.info(f"Making request to OpenDota API: {url}")
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                
                # Debug response
                logger.info(f"Response status: {response.status_code}")
                
                # Handle API errors
                if response.status_code == 429:
                    logger.warning(f"Rate limit exceeded: {response.headers}")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again later."
                    )
                elif response.status_code == 404:
                    logger.warning(f"Resource not found: {url}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Resource not found."
                    )
                elif response.status_code != 200:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"API returned status code {response.status_code}"
                    )
                
                return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error connecting to OpenDota API: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error: {str(e)}"
            )
