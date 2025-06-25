import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

async def test_supabase_connection():
    print("Starting simple Supabase connection test...")
    
    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase credentials!")
        return
    
    print(f"Supabase URL: {url}")
    print(f"Supabase Key: {key[:5]}...{key[-5:] if len(key) > 10 else ''}")
    
    try:
        # Create Supabase client
        print("Creating Supabase client...")
        client = create_client(url, key)
        
        # Test a simple query
        print("Testing simple query...")
        
        # Note: The Python Supabase client uses a different syntax for async operations
        # It returns an object that we need to call .execute() on to get the async response
        response = client.table("game_categories").select("*").execute()
        
        # Print results
        print(f"Query successful! Found {len(response.data)} game categories:")
        for category in response.data[:3]:  # Show first 3
            print(f"  - {category.get('name', 'N/A')}")
        if len(response.data) > 3:
            print(f"  - ... and {len(response.data) - 3} more")
            
        print("\n✅ Supabase connection test successful!")
        
    except Exception as e:
        print(f"\n❌ Supabase test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_supabase_connection())
