import os
import requests
from typing import Optional
import urllib3
import json

class GrokService:
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY')
        if not self.api_key:
            print("Error: GROK_API_KEY not found in environment variables")
            return
        self.api_url = "https://api.grok.ai/v1/chat/completions"
        
    def generate_email_content(self, prompt: str) -> Optional[str]:
        """Generate email content using Grok API."""
        if not self.api_key:
            print("Error: API key not initialized")
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "grok-1",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional email writer specializing in business development and software solutions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            print(f"Making request to Grok API...")
            print(f"URL: {self.api_url}")
            print(f"Headers: {json.dumps(headers, indent=2)}")
            print(f"Data: {json.dumps(data, indent=2)}")
            
            # Disable SSL verification for development
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                verify=False,
                timeout=30
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
            
            if response.status_code != 200:
                print(f"Error response: {response.text}")
                return None
                
            result = response.json()
            print(f"Response data: {json.dumps(result, indent=2)}")
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                print("No content found in response")
                return None
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None 