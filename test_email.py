#!/usr/bin/env python3

import os
from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv(override=True)

import json
import random
import requests
from gmail_service import GmailService
from config import FIREBASE_URL

def get_random_business():
    """Get a random business from Firebase."""
    try:
        response = requests.get(f"{FIREBASE_URL}/businesses.json")
        if response.status_code == 200:
            businesses = response.json()
            if businesses:
                # Convert to list of tuples (id, data)
                business_list = list(businesses.items())
                # Get a random business
                business_id, business_data = random.choice(business_list)
                print(f"Selected business: {business_data['name']} ({business_data['city']}, {business_data['state']})")
                return business_data
    except Exception as e:
        print(f"Error getting random business: {e}")
    return None

def main():
    # Initialize Gmail service
    gmail_service = GmailService()
    
    # Get test recipient from environment variables and strip whitespace
    test_recipient = os.environ.get('TEST_RECIPIENT', '').strip()
    print(f"DEBUG: Retrieved TEST_RECIPIENT from env: {test_recipient}")
    
    if not test_recipient:
        print("Error: TEST_RECIPIENT not set in environment variables")
        return
    
    # Send test email
    print(f"Sending test email to {test_recipient}...")
    success = gmail_service.send_personalized_email(test_recipient)
    
    if success:
        print("Test email sent successfully!")
    else:
        print("Failed to send test email. Please check the logs for details.")

if __name__ == "__main__":
    main() 