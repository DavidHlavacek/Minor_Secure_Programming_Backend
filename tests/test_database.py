import asyncio
import sys
import os
from dotenv import load_dotenv
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force use of the real Supabase database
os.environ["USE_MOCK_DB"] = "false"

# Import database client
from app.core.database import get_db_client, close_db

async def test_database_operations():
    """
    Test basic database operations using either Supabase or mock DB.
    """
    print("Starting database test...")
    print(f"Using mock database: {os.getenv('USE_MOCK_DB', 'false')}")
    
    # Get database client
    db = await get_db_client()
    print(f"Database client type: {type(db).__name__}")
    
    # Test table name to use
    test_table = "game_categories"
    
    try:
        # 1. Test INSERT operation
        # Use game_categories table since it doesn't require auth
        # Add timestamp to name to make it unique
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_category = {
            "name": f"Test Game Category {timestamp}",
            "description": "A test game category",
            "supported_stats": True
        }
        
        insert_result = await db.insert(test_table, test_category)
        print("\n1. INSERT RESULT:")
        print(insert_result)
        
        # Store the ID for later use
        test_id = insert_result.get('id')
        if not test_id:
            raise ValueError("Could not get ID from insert result")
        print(f"Using test_id: {test_id}")
        
        # 2. Test SELECT operation (get all)
        select_result = await db.select(test_table)
        print("\n2. SELECT ALL RESULT:")
        print(f"Found {len(select_result)} records")
        for record in select_result[:2]:  # Show first 2 records
            print(f"  - {record.get('name', 'N/A')} ({record.get('id', 'N/A')})")
        if len(select_result) > 2:
            print(f"  - ... and {len(select_result) - 2} more")
            
        # 3. Test SELECT operation (with filter)
        # Use the actual name with timestamp for the filter
        test_name = test_category["name"]
        filter_result = await db.select(test_table, {"name": test_name})
        print("\n3. SELECT WITH FILTER RESULT:")
        print(f"Found {len(filter_result)} records matching filter")
        for record in filter_result:
            print(f"  - {record.get('name', 'N/A')} ({record.get('id', 'N/A')})")
            
        # 4. Test GET BY ID operation
        byid_result = await db.get_by_id(test_table, test_id)
        print("\n4. GET BY ID RESULT:")
        print(byid_result)
        
        # 5. Test UPDATE operation
        update_data = {"description": "Updated test category description"}
        update_result = await db.update(test_table, test_id, update_data)
        print("\n5. UPDATE RESULT:")
        print(update_result)
        
        # 6. Verify update worked
        updated_record = await db.get_by_id(test_table, test_id)
        print("\n6. VERIFY UPDATE:")
        print(updated_record)
        
        # 7. Test DELETE operation
        delete_result = await db.delete(test_table, test_id)
        print("\n7. DELETE RESULT:")
        print(f"Record deleted: {delete_result}")
        
        # 8. Verify delete worked
        after_delete = await db.get_by_id(test_table, test_id)
        print("\n8. VERIFY DELETE:")
        print(f"Record exists: {after_delete is not None}")
        
        # Test passed
        print("\n✅ All database operations completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await close_db()

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the test
    asyncio.run(test_database_operations())
