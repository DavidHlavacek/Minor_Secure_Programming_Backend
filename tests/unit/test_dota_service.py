import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from app.services.external_apis.open_dota import OpenDotaService
from fastapi import HTTPException

# Sample response data for testing
SAMPLE_PLAYER_INFO = {
    "profile": {
        "account_id": 123456789,
        "personaname": "TestPlayer",
        "name": "Real Name",
        "plus": True,
        "cheese": 0,
        "avatar": "https://example.com/avatar.jpg"
    },
    "mmr_estimate": {
        "estimate": 5000
    },
    "solo_competitive_rank": "4500",
    "rank_tier": 75,  # Immortal 5000+
}

SAMPLE_RECENT_MATCHES = [
    {
        "match_id": 6548394028,
        "player_slot": 128,
        "hero_id": 1,  # Anti-Mage
        "kills": 10,
        "deaths": 2,
        "assists": 5,
        "duration": 2500,
        "game_mode": 2,
        "lobby_type": 7,
        "radiant_win": True,
        "start_time": 1656789012
    },
    {
        "match_id": 6548391234,
        "player_slot": 1,
        "hero_id": 2,  # Axe
        "kills": 5,
        "deaths": 7,
        "assists": 15,
        "duration": 3100,
        "game_mode": 2,
        "lobby_type": 7,
        "radiant_win": False,
        "start_time": 1656785678
    }
]

SAMPLE_HEROES = [
    {
        "hero_id": 1,
        "name": "npc_dota_hero_antimage",
        "localized_name": "Anti-Mage",
        "primary_attr": "agi",
        "attack_type": "Melee",
        "roles": ["Carry", "Escape", "Nuker"]
    },
    {
        "hero_id": 2,
        "name": "npc_dota_hero_axe",
        "localized_name": "Axe",
        "primary_attr": "str",
        "attack_type": "Melee",
        "roles": ["Initiator", "Durable", "Disabler", "Jungler"]
    }
]

SAMPLE_WIN_LOSS = {
    "win": 100,
    "lose": 85
}

SAMPLE_PLAYER_HEROES = [
    {
        "hero_id": 1,
        "last_played": 1656789012,
        "games": 120,
        "win": 75,
        "with_games": 30,
        "with_win": 20,
        "against_games": 40,
        "against_win": 25
    },
    {
        "hero_id": 2,
        "last_played": 1656785678,
        "games": 50,
        "win": 22,
        "with_games": 15,
        "with_win": 10,
        "against_games": 25,
        "against_win": 12
    }
]

SAMPLE_MATCH_DETAILS = {
    "match_id": 6548394028,
    "radiant_win": True,
    "duration": 2500,
    "pre_game_duration": 90,
    "start_time": 1656789012,
    "players": [
        {
            "account_id": 123456789,
            "player_slot": 128,
            "hero_id": 1,
            "kills": 10,
            "deaths": 2,
            "assists": 5,
        },
        # Other players...
    ]
}

@pytest.mark.asyncio
async def test_get_player_info():
    """Test getting player information."""
    service = OpenDotaService()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_PLAYER_INFO
        mock_get.return_value = mock_response
        
        result = await service.get_player_info("123456789")
        
        assert result == SAMPLE_PLAYER_INFO
        mock_get.assert_called_once_with(
            f"{service.base_url}/players/123456789", 
            timeout=10.0
        )


@pytest.mark.asyncio
async def test_get_player_recent_matches():
    """Test getting player's recent matches."""
    service = OpenDotaService()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_RECENT_MATCHES
        mock_get.return_value = mock_response
        
        result = await service.get_player_recent_matches("123456789", 2)
        
        assert result == SAMPLE_RECENT_MATCHES[:2]
        mock_get.assert_called_once_with(
            f"{service.base_url}/players/123456789/recentMatches", 
            timeout=10.0
        )


@pytest.mark.asyncio
async def test_get_heroes():
    """Test getting list of heroes."""
    service = OpenDotaService()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_HEROES
        mock_get.return_value = mock_response
        
        result = await service.get_heroes()
        
        assert result == SAMPLE_HEROES
        mock_get.assert_called_once_with(
            f"{service.base_url}/heroes", 
            timeout=10.0
        )


@pytest.mark.asyncio
async def test_get_player_win_loss():
    """Test getting player win/loss record."""
    service = OpenDotaService()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_WIN_LOSS
        mock_get.return_value = mock_response
        
        result = await service.get_player_win_loss("123456789")
        
        assert result == SAMPLE_WIN_LOSS
        mock_get.assert_called_once_with(
            f"{service.base_url}/players/123456789/wl", 
            timeout=10.0
        )


@pytest.mark.asyncio
async def test_get_player_heroes():
    """Test getting player hero statistics."""
    service = OpenDotaService()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_PLAYER_HEROES
        mock_get.return_value = mock_response
        
        result = await service.get_player_heroes("123456789")
        
        assert result == SAMPLE_PLAYER_HEROES
        mock_get.assert_called_once_with(
            f"{service.base_url}/players/123456789/heroes", 
            timeout=10.0
        )


@pytest.mark.asyncio
async def test_get_match_details():
    """Test getting match details."""
    service = OpenDotaService()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_MATCH_DETAILS
        mock_get.return_value = mock_response
        
        result = await service.get_match_details("6548394028")
        
        assert result == SAMPLE_MATCH_DETAILS
        mock_get.assert_called_once_with(
            f"{service.base_url}/matches/6548394028", 
            timeout=10.0
        )


@pytest.mark.asyncio
async def test_http_404_error():
    """Test handling of 404 errors."""
    service = OpenDotaService()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            await service.get_player_info("123456789")
            
        assert exc_info.value.status_code == 404
        assert "Resource not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_http_429_error():
    """Test handling of rate limit (429) errors."""
    service = OpenDotaService()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_get.return_value = mock_response
        
        with pytest.raises(HTTPException) as exc_info:
            await service.get_player_info("123456789")
            
        assert exc_info.value.status_code == 429
        assert "Rate limit" in exc_info.value.detail


@pytest.mark.asyncio
async def test_request_error():
    """Test handling of request errors."""
    service = OpenDotaService()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = httpx.RequestError("Connection error")
        
        with pytest.raises(HTTPException) as exc_info:
            await service.get_player_info("123456789")
            
        assert exc_info.value.status_code == 503
        assert "Error connecting to OpenDota API" in exc_info.value.detail


@pytest.mark.asyncio
async def test_generic_error():
    """Test handling of generic errors."""
    service = OpenDotaService()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = Exception("Unexpected error")
        
        with pytest.raises(HTTPException) as exc_info:
            await service.get_player_info("123456789")
            
        assert exc_info.value.status_code == 500
        assert "Unexpected error" in exc_info.value.detail
