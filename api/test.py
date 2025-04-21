import os
import sys
import datetime
from dotenv import load_dotenv

# Ensure .env is loaded
load_dotenv()

# Import the MistralAPI class
from mistral_wrapper import MistralAPI
from database import Database

def test_mistral_api():
    """
    Test the MistralAPI wrapper by sending a simple prompt and printing the response.
    """
    print("Testing Mistral API wrapper...")
    
    try:
        # Initialize the API with debug mode turned off
        api = MistralAPI(debug=False)
        
        # Test 1: Just prompt (will use default instructions)
        test_prompt = "What is machine learning?"
        print(f"\nTest 1 - Sending prompt with default instructions: '{test_prompt}'")
        
        # Get response with just prompt (default instructions will be applied)
        response = api.get_response(test_prompt)
        
        # Print the response
        print("\nAPI Response (with default instructions):")
        print("-" * 80)
        print(response)
        print("-" * 80)
        
        # Test 2: Prompt with custom instructions
        test_instructions = "You are an AI expert. Provide a detailed explanation with examples."
        print(f"\nTest 2 - Sending prompt with custom instructions:")
        print(f"Prompt: '{test_prompt}'")
        print(f"Instructions: '{test_instructions}'")
        
        # Get response with prompt and custom instructions
        response_with_instructions = api.get_response(test_prompt, instructions=test_instructions)
        
        # Print the response
        print("\nAPI Response (with custom instructions):")
        print("-" * 80)
        print(response_with_instructions)
        print("-" * 80)
        
        print("\nTest completed successfully!")
        return True
    
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        return False

def test_mongodb_connection():
    """
    Test the connection to MongoDB and basic database operations.
    """
    print("\n" + "="*80)
    print("Testing MongoDB Connection...")
    print("="*80)
    
    try:
        # Initialize the database connection with debug mode on
        db = Database(debug=True)
        
        # Connect to the database
        db.connect()
        
        # Test collection operations
        collection_name = "test_collection"
        
        # Insert a document
        print(f"\nInserting a document into {collection_name}...")
        test_document = {"test": "document", "value": 123, "timestamp": str(datetime.datetime.now())}
        result = db.insert_one(collection_name, test_document)
        print(f"Document inserted with ID: {result.inserted_id}")
        
        # Find the document
        print("\nFinding the inserted document...")
        document = db.find_one(collection_name, {"_id": result.inserted_id})
        print(f"Found document: {document}")
        
        # Update the document
        print("\nUpdating the document...")
        update_result = db.update_one(collection_name, {"_id": result.inserted_id}, {"$set": {"value": 456}})
        print(f"Updated {update_result.modified_count} document(s)")
        
        # Find the updated document
        print("\nFinding the updated document...")
        updated_document = db.find_one(collection_name, {"_id": result.inserted_id})
        print(f"Updated document: {updated_document}")
        
        # Delete the document
        print("\nDeleting the document...")
        delete_result = db.delete_one(collection_name, {"_id": result.inserted_id})
        print(f"Deleted {delete_result.deleted_count} document(s)")
        
        # Close the connection
        db.close()
        
        print("\nMongoDB connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nMongoDB connection test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Check if .env file exists
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print(f"Warning: .env file not found at {env_path}")
        print("Please create a .env file with MISTRAL_API_URL and MONGODB_URI defined")
        sys.exit(1)
    
    # Run the Mistral API test
    mistral_success = test_mistral_api()
    
    # Run the MongoDB connection test
    mongo_success = test_mongodb_connection()
    
    # Exit with appropriate code
    if mistral_success and mongo_success:
        print("\nAll tests completed successfully!")
        sys.exit(0)
    else:
        print("\nOne or more tests failed.")
        sys.exit(1)
