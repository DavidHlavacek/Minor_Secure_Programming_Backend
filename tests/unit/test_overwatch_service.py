import pytest
import httpx
import json
import asyncio
from unittest.mock import patch, MagicMock
from app.services.external_apis.overwatch_api import OverFastAPIService

# Sample response data for mocking
SAMPLE_PROFILE = {
    "player_name": "TestPlayer",
    "player_level": 100,
    "endorsement_level": 3,
    "avatar": "https://example.com/avatar.jpg"
}

SAMPLE_SUMMARY = {
    "quickplay": {
        "games_played": 150,
        "time_played": "50 hours"
    },
    "competitive": {
        "games_played": 75,
        "time_played": "25 hours"
    }
}

SAMPLE_COMPETITIVE = {
    "tank": {"division": "diamond", "tier": 2},
    "damage": {"division": "platinum", "tier": 1},
    "support": {"division": "gold", "tier": 3}
}

SAMPLE_HEROES = {
    "reinhardt": {"time_played": "10 hours", "games_won": 15},
    "mercy": {"time_played": "8 hours", "games_won": 12}
}

SAMPLE_HEROES_LIST = [
    {"name": "Reinhardt", "role": "tank"},
    {"name": "Mercy", "role": "support"},
    {"name": "Soldier: 76", "role": "damage"}
]

SAMPLE_MAPS = [
    {"name": "King's Row", "gamemodes": ["hybrid"]},
    {"name": "Numbani", "gamemodes": ["escort"]}
]


# Mock class for httpx.AsyncClient
class MockAsyncClient:
    def __init__(self, response_data, status_code=200):
        self.response_data = response_data
        self.status_code = status_code
        self.entered = False
    
    async def __aenter__(self):
        self.entered = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.entered = False
        return False
    
    async def get(self, url, **kwargs):
        mock_response = MagicMock()
        mock_response.status_code = self.status_code
        mock_response.raise_for_status = MagicMock()
        
        if self.status_code != 200:
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error", request=MagicMock(), response=mock_response
            )
            mock_response.text = json.dumps({"error": "Not Found"})
        
        mock_response.json = MagicMock(return_value=self.response_data)
        return mock_response


@pytest.fixture
def overwatch_service():
    return OverFastAPIService()


@pytest.mark.asyncio
async def test_get_player_profile_success(overwatch_service):
    """Test successful player profile retrieval"""
    with patch('httpx.AsyncClient', return_value=MockAsyncClient(SAMPLE_PROFILE)):
        result = await overwatch_service.get_player_profile("TestPlayer-1234")
        
        # Verify the result matches our sample data
        assert result == SAMPLE_PROFILE
        assert result["player_name"] == "TestPlayer"
        assert result["player_level"] == 100


@pytest.mark.asyncio
async def test_get_player_summary_success(overwatch_service):
    """Test successful player summary retrieval"""
    with patch('httpx.AsyncClient', return_value=MockAsyncClient(SAMPLE_SUMMARY)):
        result = await overwatch_service.get_player_summary("TestPlayer-1234")
        
        # Verify the result matches our sample data
        assert result == SAMPLE_SUMMARY
        assert "quickplay" in result
        assert "competitive" in result
        assert result["quickplay"]["games_played"] == 150


@pytest.mark.asyncio
async def test_get_player_competitive_success(overwatch_service):
    """Test successful competitive rankings retrieval"""
    with patch('httpx.AsyncClient', return_value=MockAsyncClient(SAMPLE_COMPETITIVE)):
        result = await overwatch_service.get_player_competitive("TestPlayer-1234")
        
        # Verify the result matches our sample data
        assert result == SAMPLE_COMPETITIVE
        assert "tank" in result
        assert result["tank"]["division"] == "diamond"
        assert result["damage"]["tier"] == 1


@pytest.mark.asyncio
async def test_get_player_heroes_success(overwatch_service):
    """Test successful player heroes stats retrieval"""
    with patch('httpx.AsyncClient', return_value=MockAsyncClient(SAMPLE_HEROES)):
        result = await overwatch_service.get_player_heroes("TestPlayer-1234", "quickplay")
        
        # Verify the result matches our sample data
        assert result == SAMPLE_HEROES
        assert "reinhardt" in result
        assert result["mercy"]["time_played"] == "8 hours"


@pytest.mark.asyncio
async def test_get_heroes_list_success(overwatch_service):
    """Test successful heroes list retrieval"""
    with patch('httpx.AsyncClient', return_value=MockAsyncClient(SAMPLE_HEROES_LIST)):
        result = await overwatch_service.get_heroes()
        
        # Verify the result matches our sample data
        assert result == SAMPLE_HEROES_LIST
        assert len(result) == 3
        assert result[0]["name"] == "Reinhardt"


@pytest.mark.asyncio
async def test_get_maps_success(overwatch_service):
    """Test successful maps list retrieval"""
    with patch('httpx.AsyncClient', return_value=MockAsyncClient(SAMPLE_MAPS)):
        result = await overwatch_service.get_maps()
        
        # Verify the result matches our sample data
        assert result == SAMPLE_MAPS
        assert len(result) == 2
        assert result[0]["name"] == "King's Row"


@pytest.mark.asyncio
async def test_get_combined_player_profile_success(overwatch_service):
    """Test successful combined player profile retrieval by mocking each individual method"""
    
    # Create mock implementations for each method
    overwatch_service.get_player_profile = MagicMock(return_value=asyncio.Future())
    overwatch_service.get_player_profile.return_value.set_result(SAMPLE_PROFILE)
    
    overwatch_service.get_player_summary = MagicMock(return_value=asyncio.Future())
    overwatch_service.get_player_summary.return_value.set_result(SAMPLE_SUMMARY)
    
    overwatch_service.get_player_competitive = MagicMock(return_value=asyncio.Future())
    overwatch_service.get_player_competitive.return_value.set_result(SAMPLE_COMPETITIVE)
    
    overwatch_service.get_player_heroes = MagicMock(return_value=asyncio.Future())
    overwatch_service.get_player_heroes.return_value.set_result(SAMPLE_HEROES)
    
    # Call the method under test
    result = await overwatch_service.get_combined_player_profile("TestPlayer-1234")
    
    # Verify the result
    assert "profile" in result
    assert "summary" in result
    assert "competitive" in result
    assert "heroes" in result
    
    assert result["profile"] == SAMPLE_PROFILE
    assert result["summary"] == SAMPLE_SUMMARY
    assert result["competitive"] == SAMPLE_COMPETITIVE
    assert result["heroes"] == SAMPLE_HEROES


@pytest.mark.asyncio
async def test_http_error_handling(overwatch_service):
    """Test error handling for HTTP errors"""
    # Mock a 404 response
    with patch('httpx.AsyncClient', return_value=MockAsyncClient({}, status_code=404)):
        result = await overwatch_service._make_request("any_url")
        assert "error" in result
        assert "not found" in result["error"].lower() or "private profile" in result["error"].lower()


@pytest.mark.asyncio
async def test_request_exception_handling(overwatch_service):
    """Test handling of request exceptions"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock the AsyncClient to raise an exception when get is called
        instance = MagicMock()
        mock_client.return_value.__aenter__.return_value = instance
        instance.get.side_effect = httpx.RequestError("Connection error", request=MagicMock())
        
        # Verify the exception is properly raised
        with pytest.raises(httpx.RequestError):
            await overwatch_service._make_request("any_url")
