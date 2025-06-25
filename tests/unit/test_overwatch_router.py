import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import Request, HTTPException
from fastapi.testclient import TestClient
from app.routers.specific_games.overwatch import router, get_overwatch_service
from app.middleware.auth_middleware import get_current_user

# Sample response data - same as in the service tests
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

SAMPLE_HEROES_LIST = [
    {"name": "Reinhardt", "role": "tank"},
    {"name": "Mercy", "role": "support"},
    {"name": "Soldier: 76", "role": "damage"}
]

SAMPLE_MAPS = [
    {"name": "King's Row", "gamemodes": ["hybrid"]},
    {"name": "Numbani", "gamemodes": ["escort"]}
]

# Sample user for authentication
MOCK_USER = {
    "id": "test-user-id",
    "email": "test@example.com",
    "name": "Test User"
}


# Override dependency
@pytest.fixture
def mock_service():
    """Create a mock service for testing."""
    mock = AsyncMock()
    
    # Configure mock methods
    mock.get_player_profile.return_value = SAMPLE_PROFILE
    mock.get_player_summary.return_value = SAMPLE_SUMMARY
    mock.get_player_competitive.return_value = SAMPLE_COMPETITIVE
    mock.get_heroes.return_value = SAMPLE_HEROES_LIST
    mock.get_maps.return_value = SAMPLE_MAPS
    mock.get_combined_player_profile.return_value = {
        "profile": SAMPLE_PROFILE,
        "summary": SAMPLE_SUMMARY,
        "competitive": SAMPLE_COMPETITIVE
    }
    
    return mock


# Create a TestClient with overridden dependencies
@pytest.fixture
def test_client(mock_service):
    """Create a test client with dependencies overridden."""
    from fastapi import FastAPI
    
    app = FastAPI()
    
    # Override service dependency
    async def mock_get_overwatch_service():
        return mock_service
    
    # Override authentication dependency
    async def mock_get_current_user():
        return MOCK_USER
    
    # Register the dependencies
    app.dependency_overrides[get_overwatch_service] = mock_get_overwatch_service
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    # Include the router
    app.include_router(router)
    
    return TestClient(app)


def test_get_player_profile_endpoint(test_client, mock_service):
    """Test the player profile endpoint."""
    response = test_client.get("/players/TestPlayer-1234")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_PROFILE
    }
    mock_service.get_player_profile.assert_called_once_with("TestPlayer-1234")


def test_get_player_summary_endpoint(test_client, mock_service):
    """Test the player summary endpoint."""
    response = test_client.get("/players/TestPlayer-1234/summary")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_SUMMARY
    }
    mock_service.get_player_summary.assert_called_once_with("TestPlayer-1234")


def test_get_player_competitive_endpoint(test_client, mock_service):
    """Test the player competitive endpoint."""
    response = test_client.get("/players/TestPlayer-1234/competitive")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_COMPETITIVE
    }
    mock_service.get_player_competitive.assert_called_once_with("TestPlayer-1234")


def test_get_heroes_endpoint(test_client, mock_service):
    """Test the heroes endpoint."""
    response = test_client.get("/heroes")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_HEROES_LIST
    }
    mock_service.get_heroes.assert_called_once()


def test_get_maps_endpoint(test_client, mock_service):
    """Test the maps endpoint."""
    response = test_client.get("/maps")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_MAPS
    }
    mock_service.get_maps.assert_called_once()


def test_get_combined_profile_endpoint(test_client, mock_service):
    """Test the combined profile endpoint."""
    response = test_client.get("/profile/TestPlayer-1234")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "profile" in data["data"]
    assert "summary" in data["data"]
    assert "competitive" in data["data"]
    
    mock_service.get_combined_player_profile.assert_called_once_with("TestPlayer-1234")


def test_service_error_handling(test_client, mock_service):
    """Test error handling when the service raises an exception."""
    # Configure mock to raise an exception
    mock_service.get_player_profile.side_effect = Exception("Service error")
    
    response = test_client.get("/players/TestPlayer-1234")
    
    assert response.status_code == 500
    assert "error" in response.json()
    assert not response.json()["success"]


def test_not_found_handling(test_client, mock_service):
    """Test handling of player not found errors."""
    # Configure mock to return a not found response
    mock_service.get_player_profile.return_value = {"error": "Player not found or private profile"}
    
    response = test_client.get("/players/TestPlayer-1234")
    
    assert response.status_code == 404
    assert "error" in response.json()
    assert not response.json()["success"]
