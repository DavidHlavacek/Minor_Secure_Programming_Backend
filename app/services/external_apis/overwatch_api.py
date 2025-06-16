from typing import Dict, Any, List, Optional
import httpx
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class OverFastAPIService:
    """Service for interacting with the OverFast API for Overwatch 2 data."""
    
    def __init__(self):
        self.base_url = "https://overfast-api.tekrop.fr"
    
    async def get_player_profile(self, battletag: str) -> Dict[str, Any]:
        """Get general player profile information."""
        url = f"{self.base_url}/players/{battletag}"
        return await self._make_request(url)
    
    async def get_player_summary(self, battletag: str) -> Dict[str, Any]:
        """Get player summary statistics for quick play and competitive."""
        url = f"{self.base_url}/players/{battletag}/summary"
        return await self._make_request(url)
    
    async def get_player_competitive(self, battletag: str) -> Dict[str, Any]:
        """Get player competitive rankings."""
        url = f"{self.base_url}/players/{battletag}/competitive"
        return await self._make_request(url)
    
    async def get_player_heroes(self, battletag: str, mode: str = "quickplay") -> Dict[str, Any]:
        """Get player statistics by hero.
        
        Args:
            battletag: Player's battletag
            mode: Either 'quickplay' or 'competitive'
        """
        url = f"{self.base_url}/players/{battletag}/heroes/{mode}"
        return await self._make_request(url)
    
    async def get_heroes(self) -> List[Dict[str, Any]]:
        """Get information about all heroes."""
        url = f"{self.base_url}/heroes"
        return await self._make_request(url)
    
    async def get_hero_details(self, hero_key: str) -> Dict[str, Any]:
        """Get detailed information about a specific hero."""
        url = f"{self.base_url}/heroes/{hero_key}"
        return await self._make_request(url)
    
    async def get_maps(self) -> List[Dict[str, Any]]:
        """Get information about all maps."""
        url = f"{self.base_url}/maps"
        return await self._make_request(url)
    
    async def get_combined_player_profile(self, battletag: str) -> Dict[str, Any]:
        """Get combined player profile with summary stats and competitive rankings."""
        try:
            # Get basic profile
            profile_data = await self.get_player_profile(battletag)
            
            # Get summary stats
            summary_data = await self.get_player_summary(battletag)
            
            # Get competitive rankings
            competitive_data = await self.get_player_competitive(battletag)
            
            # Get heroes data for quickplay
            heroes_data = await self.get_player_heroes(battletag, "quickplay")
            
            # Combine all data
            return {
                "profile": profile_data,
                "summary": summary_data,
                "competitive": competitive_data,
                "heroes": heroes_data
            }
        except Exception as e:
            logger.error(f"Error combining player profile data: {str(e)}")
            raise
    
    async def _make_request(self, url: str) -> Dict[str, Any]:
        """Make a request to the OverFast API."""
        try:
            logger.info(f"Making request to {url}")
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            # Special handling for 404 errors (player not found)
            if e.response.status_code == 404:
                return {"error": "Player not found or private profile"}
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
