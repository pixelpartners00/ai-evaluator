import os
import sys
from dotenv import load_dotenv

# Ensure .env is loaded
load_dotenv()

# Import the MistralAPI class
from mistral_wrapper import MistralAPI

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

if __name__ == "__main__":
    # Check if .env file exists
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_path):
        print(f"Warning: .env file not found at {env_path}")
        print("Please create a .env file with MISTRAL_API_URL defined")
        sys.exit(1)
    
    # Run the test
    success = test_mistral_api()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
