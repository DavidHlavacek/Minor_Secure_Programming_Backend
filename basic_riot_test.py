"""
Basic test for Riot API with minimal dependencies
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_basic_riot_api():
    # Get API key from environment
    api_key = os.getenv("RIOT_API_KEY")
    
    if not api_key:
        print("⚠️ No RIOT_API_KEY found in .env file!")
        return
    
    print(f"🔑 Using Riot API key: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")
    
    # Define parameters
    summoner_name = "Doublelift"
    region = "na1"
    
    # URLs to test
    summoner_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    
    # Make direct request
    async with httpx.AsyncClient() as client:
        headers = {
            "X-Riot-Token": api_key
        }
        
        print(f"\nTesting summoner lookup for '{summoner_name}'...")
        try:
            response = await client.get(summoner_url, headers=headers, timeout=30)
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Summoner data received:")
                print(f"   Name: {data.get('name')}")
                print(f"   Level: {data.get('summonerLevel')}")
                print(f"   ID: {data.get('id')[:8]}...")
                print(f"   PUUID: {data.get('puuid')[:8]}...")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Error details: {response.text}")
                
                # Common error codes
                if response.status_code == 401:
                    print("This is an AUTHENTICATION error - your API key is invalid or expired")
                elif response.status_code == 403:
                    print("This is an AUTHORIZATION error - your API key might not have permission for this endpoint")
                elif response.status_code == 404:
                    print(f"Summoner '{summoner_name}' not found in region {region}")
                elif response.status_code == 429:
                    print("Rate limit exceeded - too many requests")
            
        except Exception as e:
            print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_basic_riot_api())
