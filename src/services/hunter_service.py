import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HunterService:
    def __init__(self):
        self.api_key = os.getenv('HUNTER_API_KEY')
        self.base_url = "https://api.hunter.io/v2"

    def verify_email(self, email):
        """Verify if an email address is valid using Hunter.io API."""
        try:
            print(f"DEBUG: Verifying email: {email}")
            
            # Make request to Hunter.io API
            response = requests.get(
                f"{self.base_url}/email-verifier",
                params={
                    "email": email,
                    "api_key": self.api_key
                }
            )

            print(f"DEBUG: Hunter.io response status: {response.status_code}")
            print(f"DEBUG: Hunter.io response: {response.text}")

            if response.status_code == 200:
                data = response.json()
                result = data.get('data', {})
                
                # Check verification status
                status = result.get('status')
                score = result.get('score', 0)
                
                # Consider email valid if:
                # 1. Status is 'valid' or 'accept-all'
                # 2. Score is above 50
                is_valid = (status in ['valid', 'accept-all']) and score > 50
                
                print(f"DEBUG: Email verification result - Status: {status}, Score: {score}, Valid: {is_valid}")
                return is_valid
            else:
                print(f"Failed to verify email: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error verifying email: {e}")
            return False

    def find_email(self, domain, first_name=None, last_name=None):
        """Find email address for a domain using Hunter.io API."""
        try:
            print(f"DEBUG: Finding email for domain: {domain}")
            
            # Make request to Hunter.io API
            response = requests.get(
                f"{self.base_url}/email-finder",
                params={
                    "domain": domain,
                    "first_name": first_name,
                    "last_name": last_name,
                    "api_key": self.api_key
                }
            )

            print(f"DEBUG: Hunter.io response status: {response.status_code}")
            print(f"DEBUG: Hunter.io response: {response.text}")

            if response.status_code == 200:
                data = response.json()
                result = data.get('data', {})
                
                # Get the email and confidence score
                email = result.get('email')
                confidence = result.get('score', 0)
                
                # Only return email if confidence is high enough
                if email and confidence > 50:
                    print(f"DEBUG: Found email: {email} (confidence: {confidence})")
                    return email
                else:
                    print(f"DEBUG: No valid email found (confidence: {confidence})")
                    return None
            else:
                print(f"Failed to find email: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Error finding email: {e}")
            return None 