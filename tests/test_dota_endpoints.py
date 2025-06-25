"""
Dota API Endpoints Test Script

This script tests the Dota API endpoints in our backend application.
"""
import httpx
import asyncio
import json
from typing import Dict, Any

# Base URL for our API
BASE_URL = "http://localhost:8000/api/v1/dota"

# Pro player nicknames to test
PLAYERS = [
    "arteezy",  # Arteezy
    "miracle",  # Miracle-
    "sumail"    # SumaiL
]

async def test_player_info(player_name: str):
    """Test the player info endpoint"""
    print(f"\n=== Testing Player Info for {player_name} ===")
    url = f"{BASE_URL}/players/{player_name}"
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"Calling endpoint: {url}")
            response = await client.get(url, timeout=30.0)
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    player_data = data.get("data", {})
                    profile = player_data.get("profile", {})
                    
                    print("✅ SUCCESS: Player info retrieved")
                    print(f"  Name: {profile.get('personaname', 'Unknown')}")
                    print(f"  Account ID: {player_data.get('account_id', 'Unknown')}")
                    print(f"  Country: {profile.get('loccountrycode', 'Unknown')}")
                    return True
                else:
                    print("❌ FAILED: API returned success=False")
            else:
                print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    return False

async def test_win_loss(player_name: str):
    """Test the win/loss endpoint"""
    print(f"\n=== Testing Win/Loss for {player_name} ===")
    url = f"{BASE_URL}/players/{player_name}/win-loss"
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"Calling endpoint: {url}")
            response = await client.get(url, timeout=30.0)
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    wl_data = data.get("data", {})
                    wins = wl_data.get("win", 0)
                    losses = wl_data.get("lose", 0)
                    
                    print("✅ SUCCESS: Win/Loss retrieved")
                    print(f"  Wins: {wins}")
                    print(f"  Losses: {losses}")
                    print(f"  Total Games: {wins + losses}")
                    if wins + losses > 0:
                        win_rate = (wins / (wins + losses)) * 100
                        print(f"  Win Rate: {win_rate:.2f}%")
                    return True
                else:
                    print("❌ FAILED: API returned success=False")
            else:
                print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    return False

async def test_recent_matches(player_name: str):
    """Test the recent matches endpoint"""
    print(f"\n=== Testing Recent Matches for {player_name} ===")
    url = f"{BASE_URL}/players/{player_name}/recent-matches?limit=5"
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"Calling endpoint: {url}")
            response = await client.get(url, timeout=30.0)
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    matches = data.get("data", [])
                    
                    print(f"✅ SUCCESS: Retrieved {len(matches)} recent matches")
                    for i, match in enumerate(matches[:3]):  # Show max 3 matches
                        print(f"  Match {i+1}:")
                        print(f"    Hero ID: {match.get('hero_id', 'Unknown')}")
                        print(f"    K/D/A: {match.get('kills', 0)}/{match.get('deaths', 0)}/{match.get('assists', 0)}")
                        match_id = match.get('match_id', 'Unknown')
                        print(f"    Match ID: {match_id}")
                    return True, matches[0].get('match_id') if matches else None
                else:
                    print("❌ FAILED: API returned success=False")
            else:
                print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    return False, None

async def test_heroes():
    """Test the heroes endpoint"""
    print("\n=== Testing Heroes Endpoint ===")
    url = f"{BASE_URL}/heroes"
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"Calling endpoint: {url}")
            response = await client.get(url, timeout=30.0)
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    heroes = data.get("data", [])
                    
                    print(f"✅ SUCCESS: Retrieved {len(heroes)} heroes")
                    
                    # Show a few heroes
                    import random
                    sample_heroes = random.sample(heroes, min(5, len(heroes)))
                    for i, hero in enumerate(sample_heroes):
                        print(f"  Hero {i+1}: {hero.get('localized_name', 'Unknown')}")
                        print(f"    Primary Attr: {hero.get('primary_attr', 'Unknown')}")
                        print(f"    Attack Type: {hero.get('attack_type', 'Unknown')}")
                        print(f"    Roles: {', '.join(hero.get('roles', []))}")
                    return True
                else:
                    print("❌ FAILED: API returned success=False")
            else:
                print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    return False

async def test_public_matches():
    """Test the public matches endpoint"""
    print("\n=== Testing Public Matches Endpoint ===")
    url = f"{BASE_URL}/public-matches?limit=5"
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"Calling endpoint: {url}")
            response = await client.get(url, timeout=30.0)
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    matches = data.get("data", [])
                    
                    print(f"✅ SUCCESS: Retrieved {len(matches)} public matches")
                    for i, match in enumerate(matches[:3]):  # Show max 3 matches
                        print(f"  Match {i+1}:")
                        print(f"    Match ID: {match.get('match_id', 'Unknown')}")
                        print(f"    Duration: {match.get('duration', 0) // 60} minutes")
                        print(f"    Winner: {'Radiant' if match.get('radiant_win') else 'Dire'}")
                    
                    return True, matches[0].get('match_id') if matches else None
                else:
                    print("❌ FAILED: API returned success=False")
            else:
                print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    return False, None

async def test_match_details(match_id):
    """Test the match details endpoint"""
    if not match_id:
        print("\n=== Skipping Match Details Test (No Match ID) ===")
        return False
        
    print(f"\n=== Testing Match Details for {match_id} ===")
    url = f"{BASE_URL}/matches/{match_id}"
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"Calling endpoint: {url}")
            response = await client.get(url, timeout=30.0)
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    match = data.get("data", {})
                    
                    print("✅ SUCCESS: Match details retrieved")
                    print(f"  Match ID: {match.get('match_id', 'Unknown')}")
                    print(f"  Duration: {match.get('duration', 0) // 60} minutes")
                    print(f"  Game Mode: {match.get('game_mode_name', 'Unknown')}")
                    print(f"  Winner: {'Radiant' if match.get('radiant_win', False) else 'Dire'}")
                    
                    # Show player info
                    players = match.get('players', [])
                    if players:
                        print(f"  Players: {len(players)}")
                        for i, player in enumerate(players[:5]):  # Just show first 5 players
                            print(f"    Player {i+1}: Hero ID {player.get('hero_id', 'Unknown')}")
                            print(f"      K/D/A: {player.get('kills', 0)}/{player.get('deaths', 0)}/{player.get('assists', 0)}")
                    return True
                else:
                    print("❌ FAILED: API returned success=False")
            else:
                print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    return False

async def test_player_profile(player_name: str):
    """Test the player profile endpoint (combined data)"""
    print(f"\n=== Testing Complete Player Profile for {player_name} ===")
    url = f"{BASE_URL}/profile/{player_name}"
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"Calling endpoint: {url}")
            response = await client.get(url, timeout=30.0)
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    profile_data = data.get("data", {})
                    
                    print("✅ SUCCESS: Complete profile retrieved")
                    
                    # Player info
                    player = profile_data.get("player", {})
                    profile = player.get("profile", {})
                    print(f"  Name: {profile.get('personaname', 'Unknown')}")
                    print(f"  Account ID: {player.get('account_id', 'Unknown')}")
                    
                    # Win/Loss
                    wl = profile_data.get("win_loss", {})
                    wins = wl.get("win", 0)
                    losses = wl.get("lose", 0)
                    print(f"  Win/Loss: {wins}/{losses}")
                    
                    # Recent matches
                    matches = profile_data.get("recent_matches", [])
                    print(f"  Recent Matches: {len(matches)}")
                    
                    # Top heroes
                    heroes = profile_data.get("top_heroes", [])
                    print(f"  Top Heroes: {len(heroes)}")
                    
                    return True
                else:
                    print("❌ FAILED: API returned success=False")
            else:
                print(f"❌ FAILED: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    return False

async def main():
    """Run all tests"""
    print("========================================")
    print("       DOTA API ENDPOINTS TEST          ")
    print("========================================")
    print("\nMake sure your backend server is running!")
    print("Testing against URL:", BASE_URL)
    
    results = {}
    
    # Test hero list (doesn't need a player)
    results["heroes"] = await test_heroes()
    
    # Test a pro player - full suite of tests
    player = PLAYERS[0]  # Test with arteezy
    results[f"player_{player}_info"] = await test_player_info(player)
    results[f"player_{player}_wl"] = await test_win_loss(player)
    results[f"player_{player}_matches"], match_id = await test_recent_matches(player)
    
    # Test match details if we have a match ID
    results["match_details"] = await test_match_details(match_id)
    
    # Test public matches
    results["public_matches"], another_match_id = await test_public_matches()
    if not match_id:
        # Only test another match details if we didn't get a match ID from recent matches
        results["match_details_alt"] = await test_match_details(another_match_id)
    
    # Test player profile (combined endpoint)
    results["player_profile"] = await test_player_profile(player)
    
    # Print summary
    print("\n========================================")
    print("           TEST RESULTS                 ")
    print("========================================")
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"Tests Passed: {success_count}/{total_count} ({success_count/total_count*100:.0f}%)")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    if success_count == total_count:
        print("\n🎉 All tests passed! The OpenDota API integration is working correctly.")
    else:
        print(f"\n⚠️ {total_count - success_count} tests failed. Check the logs above for details.")
    
if __name__ == "__main__":
    asyncio.run(main())
