import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import Request, HTTPException
from fastapi.testclient import TestClient
from app.routers.specific_games.dota import router

# Sample response data - same as in the service tests
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
        "hero_id": 1,
        "kills": 10,
        "deaths": 2,
        "assists": 5,
    },
    {
        "match_id": 6548391234,
        "player_slot": 1,
        "hero_id": 2,
        "kills": 5,
        "deaths": 7,
        "assists": 15,
    }
]

SAMPLE_WIN_LOSS = {
    "win": 100,
    "lose": 85
}

SAMPLE_PLAYER_HEROES = [
    {
        "hero_id": 1,
        "games": 120,
        "win": 75,
    },
    {
        "hero_id": 2,
        "games": 50,
        "win": 22,
    }
]

SAMPLE_HEROES = [
    {
        "hero_id": 1,
        "name": "npc_dota_hero_antimage",
        "localized_name": "Anti-Mage",
    },
    {
        "hero_id": 2,
        "name": "npc_dota_hero_axe",
        "localized_name": "Axe",
    }
]

SAMPLE_MATCH_DETAILS = {
    "match_id": 6548394028,
    "radiant_win": True,
    "duration": 2500,
}

# Sample user for authentication
MOCK_USER = {
    "user_id": "test-user-id",
    "email": "test@example.com",
    "role": "user",
    "exp": 1717027200  # Some future time
}


# Create a mock OpenDotaService
@pytest.fixture
def mock_service():
    """Create a mock service for testing."""
    mock = AsyncMock()
    
    # Configure mock methods
    mock.get_player_info.return_value = SAMPLE_PLAYER_INFO
    mock.get_player_recent_matches.return_value = SAMPLE_RECENT_MATCHES
    mock.get_player_win_loss.return_value = SAMPLE_WIN_LOSS
    mock.get_player_heroes.return_value = SAMPLE_PLAYER_HEROES
    mock.get_heroes.return_value = SAMPLE_HEROES
    mock.get_hero_stats.return_value = SAMPLE_HEROES  # Using same data for simplicity
    mock.get_match_details.return_value = SAMPLE_MATCH_DETAILS
    mock.get_public_matches.return_value = [SAMPLE_MATCH_DETAILS]
    mock.get_pro_players.return_value = [SAMPLE_PLAYER_INFO]
    mock.get_pro_matches.return_value = [SAMPLE_MATCH_DETAILS]
    
    return mock


# Create a TestClient with overridden dependencies
@pytest.fixture
def test_client(mock_service):
    """Create a test client with dependencies overridden."""
    from fastapi import FastAPI, Depends
    from app.middleware.auth_middleware import get_current_user, get_optional_user
    
    app = FastAPI()
    
    # Override service dependency
    async def mock_get_dota_service():
        return mock_service
    
    # Override service instantiation
    with patch("app.services.external_apis.open_dota.OpenDotaService") as mock_class:
        mock_class.return_value = mock_service
        
        # Override authentication dependency
        async def mock_get_current_user():
            return MOCK_USER
            
        async def mock_get_optional_user():
            return MOCK_USER
        
        # Register the dependencies
        app.dependency_overrides[get_current_user] = mock_get_current_user
        app.dependency_overrides[get_optional_user] = mock_get_optional_user
        
        # Include the router
        app.include_router(router)
        
        return TestClient(app)


def test_get_player_info_endpoint(test_client, mock_service):
    """Test the player info endpoint."""
    response = test_client.get("/players/123456789")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_PLAYER_INFO
    }
    mock_service.get_player_info.assert_called_once_with("123456789")


def test_get_recent_matches_endpoint(test_client, mock_service):
    """Test the recent matches endpoint."""
    response = test_client.get("/players/123456789/recent-matches?limit=5")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_RECENT_MATCHES
    }
    mock_service.get_player_recent_matches.assert_called_once_with("123456789", 5)


def test_get_win_loss_endpoint(test_client, mock_service):
    """Test the win/loss endpoint."""
    response = test_client.get("/players/123456789/win-loss")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_WIN_LOSS
    }
    mock_service.get_player_win_loss.assert_called_once_with("123456789")


def test_get_player_heroes_endpoint(test_client, mock_service):
    """Test the player heroes endpoint."""
    response = test_client.get("/players/123456789/heroes")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_PLAYER_HEROES
    }
    mock_service.get_player_heroes.assert_called_once_with("123456789")


def test_get_heroes_endpoint(test_client, mock_service):
    """Test the heroes endpoint."""
    response = test_client.get("/heroes")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_HEROES
    }
    mock_service.get_heroes.assert_called_once()


def test_get_hero_stats_endpoint(test_client, mock_service):
    """Test the hero stats endpoint."""
    response = test_client.get("/hero-stats")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_HEROES
    }
    mock_service.get_hero_stats.assert_called_once()


def test_get_match_details_endpoint(test_client, mock_service):
    """Test the match details endpoint."""
    response = test_client.get("/matches/6548394028")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": SAMPLE_MATCH_DETAILS
    }
    mock_service.get_match_details.assert_called_once_with("6548394028")


def test_get_public_matches_endpoint(test_client, mock_service):
    """Test the public matches endpoint."""
    response = test_client.get("/public-matches")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": [SAMPLE_MATCH_DETAILS]
    }
    mock_service.get_public_matches.assert_called_once_with(10)  # Default limit


def test_get_pro_players_endpoint(test_client, mock_service):
    """Test the pro players endpoint."""
    response = test_client.get("/pro-players")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": [SAMPLE_PLAYER_INFO]
    }
    mock_service.get_pro_players.assert_called_once()


def test_get_pro_matches_endpoint(test_client, mock_service):
    """Test the pro matches endpoint."""
    response = test_client.get("/pro-matches")
    
    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": [SAMPLE_MATCH_DETAILS]
    }
    mock_service.get_pro_matches.assert_called_once_with(10)  # Default limit


def test_get_player_profile_endpoint(test_client, mock_service):
    """Test the player profile endpoint."""
    response = test_client.get("/profile/123456789")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "player" in data["data"]
    assert "win_loss" in data["data"]
    assert "recent_matches" in data["data"]
    assert "top_heroes" in data["data"]
    
    mock_service.get_player_info.assert_called_once_with("123456789")
    mock_service.get_player_recent_matches.assert_called_once_with("123456789", 5)
    mock_service.get_player_win_loss.assert_called_once_with("123456789")
    mock_service.get_player_heroes.assert_called_once_with("123456789")


def test_pro_player_nickname_resolution(test_client, mock_service):
    """Test that pro player nicknames are properly resolved to IDs."""
    # Reset the mock to clear previous calls
    mock_service.get_player_info.reset_mock()
    
    # Call with a pro player nickname that should be in PRO_PLAYERS dictionary
    response = test_client.get("/players/arteezy")
    
    assert response.status_code == 200
    # The ID for arteezy should be looked up (it's 86745912 in the code)
    mock_service.get_player_info.assert_called_once_with("86745912")
