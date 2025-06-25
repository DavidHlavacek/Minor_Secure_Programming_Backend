import asyncio
import aiohttp
import json
import sys

# Sample battletags to test (known public profiles)
TEST_BATTLETAGS = [
    "WarDevil-11626",  # From the example in your request
    "Krusher99-1234", # For error testing
]

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

async def make_request(session, url):
    """Make a request to the API and return the response."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error {response.status} for {url}: {await response.text()}")
                return None
    except Exception as e:
        print(f"Exception for {url}: {str(e)}")
        return None

async def test_player_profile(session, battletag):
    """Test the player profile endpoint."""
    print(f"\n--- Testing Player Profile for {battletag} ---")
    url = f"{BASE_URL}/overwatch/players/{battletag}"
    response = await make_request(session, url)
    
    if response and response.get("success"):
        data = response.get("data")
        print(f"Player name: {data.get('player_name', 'unknown')}")
        print(f"Level: {data.get('player_level', 'unknown')}")
        print(f"Endorsement: {data.get('endorsement_level', 'unknown')}")
        
        # Testing avatar URL
        avatar = data.get('avatar')
        if avatar:
            print(f"Avatar URL exists: Yes")
        else:
            print(f"Avatar URL exists: No")
            
        print("Profile test: SUCCESS")
        return True
    else:
        if response and "not found" in str(response).lower():
            print(f"Profile test: SKIPPED - Player not found or private profile")
        else:
            print(f"Profile test: FAILED")
        return False

async def test_player_summary(session, battletag):
    """Test the player summary endpoint."""
    print(f"\n--- Testing Player Summary for {battletag} ---")
    url = f"{BASE_URL}/overwatch/players/{battletag}/summary"
    response = await make_request(session, url)
    
    if response and response.get("success"):
        data = response.get("data")
        print("Game modes available:")
        for mode in data:
            print(f"- {mode}")
        
        if "competitive" in data:
            print("\nCompetitive stats:")
            comp_stats = data.get("competitive", {})
            for category, stats in comp_stats.items():
                print(f"- {category}: {stats}")
                
        if "quickplay" in data:
            print("\nQuickplay stats:")
            qp_stats = data.get("quickplay", {})
            for category, stats in qp_stats.items():
                print(f"- {category}: {stats}")
        
        print("Summary test: SUCCESS")
        return True
    else:
        if response and "not found" in str(response).lower():
            print(f"Summary test: SKIPPED - Player not found or private profile")
        else:
            print(f"Summary test: FAILED")
        return False

async def test_player_competitive(session, battletag):
    """Test the player competitive endpoint."""
    print(f"\n--- Testing Player Competitive for {battletag} ---")
    url = f"{BASE_URL}/overwatch/players/{battletag}/competitive"
    response = await make_request(session, url)
    
    if response and response.get("success"):
        data = response.get("data")
        print("Competitive roles:")
        for role, rank in data.items():
            if isinstance(rank, dict):
                rank_info = f"{rank.get('division', 'unknown')} {rank.get('tier', '')}"
                print(f"- {role}: {rank_info}")
            else:
                print(f"- {role}: {rank}")
        
        print("Competitive test: SUCCESS")
        return True
    else:
        if response and "not found" in str(response).lower():
            print(f"Competitive test: SKIPPED - Player not found or private profile")
        else:
            print(f"Competitive test: FAILED")
        return False

async def test_heroes_list(session):
    """Test the heroes list endpoint."""
    print("\n--- Testing Heroes List ---")
    url = f"{BASE_URL}/overwatch/heroes"
    response = await make_request(session, url)
    
    if response and response.get("success"):
        data = response.get("data")
        print(f"Total heroes: {len(data)}")
        print("Example heroes:")
        for i, hero in enumerate(data[:5]):  # Print first 5 heroes
            print(f"- {hero.get('name', 'unknown')} (Role: {hero.get('role', 'unknown')})")
        
        print("Heroes test: SUCCESS")
        return True
    else:
        print(f"Heroes test: FAILED")
        return False

async def test_maps_list(session):
    """Test the maps list endpoint."""
    print("\n--- Testing Maps List ---")
    url = f"{BASE_URL}/overwatch/maps"
    response = await make_request(session, url)
    
    if response and response.get("success"):
        data = response.get("data")
        print(f"Total maps: {len(data)}")
        print("Example maps:")
        for i, map_data in enumerate(data[:5]):  # Print first 5 maps
            print(f"- {map_data.get('name', 'unknown')} (Type: {map_data.get('gamemodes', [])})")
        
        print("Maps test: SUCCESS")
        return True
    else:
        print(f"Maps test: FAILED")
        return False

async def test_combined_profile(session, battletag):
    """Test the combined player profile endpoint."""
    print(f"\n--- Testing Combined Profile for {battletag} ---")
    url = f"{BASE_URL}/overwatch/profile/{battletag}"
    response = await make_request(session, url)
    
    if response and response.get("success"):
        data = response.get("data")
        sections = data.keys()
        print(f"Profile sections available: {', '.join(sections)}")
        
        if "profile" in data:
            profile = data.get("profile")
            print(f"Player name: {profile.get('player_name', 'unknown')}")
            print(f"Level: {profile.get('player_level', 'unknown')}")
        
        if "competitive" in data:
            print("Competitive data available: Yes")
            
        if "summary" in data:
            print("Summary data available: Yes")
            
        if "heroes" in data:
            print("Heroes data available: Yes")
        
        print("Combined profile test: SUCCESS")
        return True
    else:
        if response and "not found" in str(response).lower():
            print(f"Combined profile test: SKIPPED - Player not found or private profile")
        else:
            print(f"Combined profile test: FAILED")
        return False

async def run_tests():
    """Run all tests."""
    async with aiohttp.ClientSession() as session:
        print("=== STARTING OVERWATCH API TESTS ===")
        
        # Test general endpoints
        await test_heroes_list(session)
        await test_maps_list(session)
        
        # Test player-specific endpoints for each test battletag
        for battletag in TEST_BATTLETAGS:
            print(f"\n=== TESTING BATTLETAG: {battletag} ===")
            await test_player_profile(session, battletag)
            await test_player_summary(session, battletag)
            await test_player_competitive(session, battletag)
            await test_combined_profile(session, battletag)

        print("\n=== OVERWATCH API TESTS COMPLETE ===")

if __name__ == "__main__":
    try:
        # Run the tests
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        sys.exit(1)
