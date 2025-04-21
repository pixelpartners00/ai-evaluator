import os
import requests
from dotenv import load_dotenv
import urllib.parse
import json

class MistralAPI:
    def __init__(self, debug=False):
        # Load environment variables
        load_dotenv()
        self.api_url = os.getenv("MISTRAL_API_URL")
        self.debug = debug
        
        if not self.api_url:
            raise ValueError("MISTRAL_API_URL is not set in the .env file")
    
    def get_response(self, prompt, instructions=None):
        """
        Send a prompt to the Mistral LLM API and get the response.
        
        Args:
            prompt (str): The prompt to send to the API
            instructions (str, optional): Instructions for how the model should respond
            
        Returns:
            str: The response from the LLM
            
        Raises:
            Exception: If there's an error with the API request
        """
        try:
            # URL encode the prompt and instructions
            encoded_prompt = urllib.parse.quote(prompt)
            
            # Set default instructions if none provided
            if instructions is None:
                instructions = "You are a respectful and helpful assistant. Respond with only the answer to the question in a few words of conversational English. Do not repeat the question."
            
            # URL encode instructions
            encoded_instructions = urllib.parse.quote(instructions)
            
            # Construct the endpoint URL
            endpoint_url = f"{self.api_url}/get_response?prompt={encoded_prompt}&instructions={encoded_instructions}"
            
            if self.debug:
                print(f"Sending request to: {endpoint_url}")
                
            response = requests.get(endpoint_url)
            
            if self.debug:
                print(f"Status code: {response.status_code}")
                print(f"Response content: {response.content[:200]}...")
            
            response.raise_for_status()
            
            # Try to parse as JSON first
            try:
                data = response.json()
                
                # Handle different response types
                if isinstance(data, dict):
                    # If it's a dictionary, try to get the "response" field
                    return data.get("response", response.text)
                elif isinstance(data, list):
                    # If it's a list (like in the AI test generation case), return it directly
                    return json.dumps(data)
                else:
                    # For any other type, convert to string
                    return str(data)
            except ValueError:
                # If not JSON, return the raw text response
                if self.debug:
                    print("Response is not in JSON format. Returning raw text response.")
                return response.text
                
        except requests.exceptions.RequestException as req_err:
            if self.debug:
                print(f"Request error: {str(req_err)}")
            raise Exception(f"Error calling Mistral API: {str(req_err)}")
        except Exception as e:
            if self.debug:
                print(f"Unexpected error: {str(e)}")
            raise Exception(f"Error calling Mistral API: {str(e)}")
