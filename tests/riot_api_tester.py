#!/usr/bin/env python
"""
Riot API Tester - Test access to various Riot API endpoints with your API key
"""
import os
import httpx
import asyncio
from dotenv import load_dotenv
from typing import Dict, Any, List

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("RIOT_API_KEY")
if not API_KEY:
    raise ValueError("No RIOT_API_KEY found in environment variables")

print(f"Using API key: {API_KEY[:5]}...")

# Headers for API requests
headers = {
    "X-Riot-Token": API_KEY,
    "Accept": "application/json",
    "User-Agent": "MinorSecureProgramming/1.0"
}

# Test endpoints - add more as needed
TEST_ENDPOINTS = [
    {
        "name": "Champion Rotations",
        "url": "https://euw1.api.riotgames.com/lol/platform/v3/champion-rotations",
        "description": "Get current free champion rotation"
    },
    {
        "name": "Summoner by Name",
        "url": "https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Caedrel",
        "description": "Get summoner info by name"
    },
    {
        "name": "League Entries",
        "url": "https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{encrypted_summoner_id}",
        "description": "Get ranked stats - requires summoner ID",
        "depends_on": "Summoner by Name",
        "extract_value": "id"
    },
    {
        "name": "Champion Mastery",
        "url": "https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{encrypted_puuid}",
        "description": "Get champion mastery - requires PUUID",
        "depends_on": "Summoner by Name",
        "extract_value": "puuid"
    },
    {
        "name": "Recent Matches",
        "url": "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{encrypted_puuid}/ids?count=5",
        "description": "Get recent matches - requires PUUID",
        "depends_on": "Summoner by Name",
        "extract_value": "puuid"
    },
    {
        "name": "Match Details",
        "url": "https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}",
        "description": "Get match details - requires match ID",
        "depends_on": "Recent Matches",
        "extract_value": "0"  # Take first match ID
    },
    {
        "name": "Platform Data",
        "url": "https://euw1.api.riotgames.com/lol/status/v4/platform-data",
        "description": "Get server status"
    }
]

async def test_endpoint(endpoint: Dict[str, Any], values: Dict[str, Any]) -> Dict[str, Any]:
    """Test a single API endpoint"""
    url = endpoint["url"]
    
    # Handle dependencies by replacing placeholders with values
    if "depends_on" in endpoint:
        dependency = endpoint["depends_on"]
        if dependency not in values:
            return {
                "name": endpoint["name"],
                "status": "Skipped",
                "message": f"Dependency '{dependency}' not available"
            }
        
        extract_value = endpoint.get("extract_value", "id")
        try:
            # Handle indexed values (for lists)
            if extract_value.isdigit():
                placeholder_value = values[dependency][int(extract_value)]
            else:
                placeholder_value = values[dependency].get(extract_value)
                
            if placeholder_value:
                # Replace placeholder in URL
                if "{encrypted_summoner_id}" in url:
                    url = url.replace("{encrypted_summoner_id}", placeholder_value)
                if "{encrypted_puuid}" in url:
                    url = url.replace("{encrypted_puuid}", placeholder_value)
                if "{match_id}" in url:
                    url = url.replace("{match_id}", placeholder_value)
            else:
                return {
                    "name": endpoint["name"],
                    "status": "Skipped",
                    "message": f"Could not extract '{extract_value}' from dependency"
                }
        except (KeyError, IndexError) as e:
            return {
                "name": endpoint["name"],
                "status": "Skipped",
                "message": f"Error extracting value: {str(e)}"
            }
    
    # Make API request
    try:
        async with httpx.AsyncClient() as client:
            print(f"Testing {endpoint['name']}: {url}")
            response = await client.get(url, headers=headers, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": endpoint["name"],
                    "status": "Success",
                    "status_code": response.status_code,
                    "data": data
                }
            else:
                return {
                    "name": endpoint["name"],
                    "status": "Failed",
                    "status_code": response.status_code,
                    "message": response.text
                }
    except Exception as e:
        return {
            "name": endpoint["name"],
            "status": "Error",
            "message": str(e)
        }

async def main():
    """Test all endpoints"""
    print("Starting Riot API tests...\n")
    
    # Store successful responses for dependent requests
    successful_values = {}
    results = []
    
    for endpoint in TEST_ENDPOINTS:
        result = await test_endpoint(endpoint, successful_values)
        results.append(result)
        
        # Store successful response for dependencies
        if result.get("status") == "Success":
            successful_values[endpoint["name"]] = result.get("data")
        
        # Print result
        print(f"\n--- {result['name']} ---")
        print(f"Status: {result.get('status')}")
        
        if result.get("status_code"):
            print(f"Status Code: {result.get('status_code')}")
        
        if result.get("message"):
            print(f"Message: {result.get('message')}")
        
        # Print first few items of data (if available)
        if result.get("data") and result.get("status") == "Success":
            data = result.get("data")
            if isinstance(data, dict):
                print("Data preview:")
                for key, value in list(data.items())[:5]:
                    preview = str(value)
                    if len(preview) > 100:
                        preview = preview[:100] + "..."
                    print(f"  {key}: {preview}")
                if len(data) > 5:
                    print(f"  ... {len(data) - 5} more keys")
            elif isinstance(data, list):
                print(f"Data preview: {len(data)} items")
                for i, item in enumerate(data[:3]):
                    preview = str(item)
                    if len(preview) > 100:
                        preview = preview[:100] + "..."
                    print(f"  [{i}] {preview}")
                if len(data) > 3:
                    print(f"  ... {len(data) - 3} more items")
        
        print("---\n")
    
    # Summary
    success_count = sum(1 for r in results if r.get("status") == "Success")
    fail_count = sum(1 for r in results if r.get("status") == "Failed")
    error_count = sum(1 for r in results if r.get("status") == "Error")
    skip_count = sum(1 for r in results if r.get("status") == "Skipped")
    
    print(f"\nSUMMARY:")
    print(f"Total endpoints tested: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Errors: {error_count}")
    print(f"Skipped: {skip_count}")

if __name__ == "__main__":
    asyncio.run(main())
