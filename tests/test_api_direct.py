#!/usr/bin/env python
"""
Test script to directly call Riot API with the key from .env
"""
import os
import httpx
import asyncio
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("RIOT_API_KEY")
if not API_KEY:
    print("Error: No RIOT_API_KEY found in environment variables")
    exit(1)

print(f"Using API key: {API_KEY[:5]}...")

# Test summoner endpoint for a known player
async def test_summoner_endpoint():
    summoner_name = "Caedrel"  # Example pro player
    url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    
    headers = {
        "X-Riot-Token": API_KEY
    }
    
    print(f"Testing direct API call to: {url}")
    print(f"Using headers: {headers}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
            
            if response.status_code == 200:
                data = response.json()
                print("\nSuccess! Summoner data:")
                print(json.dumps(data, indent=2))
                return True
            else:
                print(f"\nError response: {response.text}")
                return False
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return False

# Test multiple summoner names
async def test_multiple_summoners():
    summoner_names = ["StefanRivexRO", "Caedrel", "Jankos", "Caps", "Rekkles"]
    
    print("\nTesting multiple summoner names:")
    for name in summoner_names:
        url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}"
        headers = {"X-Riot-Token": API_KEY}
        
        try:
            async with httpx.AsyncClient() as client:
                print(f"\nTrying summoner: {name}")
                response = await client.get(url, headers=headers, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ SUCCESS for {name}: {data.get('name')} (Level {data.get('summonerLevel')})")
                else:
                    print(f"❌ FAILED for {name}: Status {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ ERROR for {name}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_summoner_endpoint())
    asyncio.run(test_multiple_summoners())
