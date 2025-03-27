#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import json
import requests
from gmail_service import GmailService
from config import FIREBASE_URL

# Load environment variables before any other imports
load_dotenv(override=True)

def get_test_business():
    """Get a specific business from Firebase for testing."""
    try:
        response = requests.get(f"{FIREBASE_URL}/businesses.json")
        if response.status_code == 200:
            businesses = response.json()
            if businesses:
                # Get the first business that hasn't received an email yet
                for business_id, data in businesses.items():
                    if not data.get('email_sent', False):
                        print(f"Selected test business: {data['name']} ({data['city']}, {data['state']})")
                        return business_id, data
        print(f"Error getting businesses: {response.status_code}")
        return None, None
    except Exception as e:
        print(f"Error accessing Firebase: {e}")
        return None, None

def mark_email_sent(business_id):
    """Mark a business as having received an email in Firebase."""
    try:
        # Update the business record to mark email as sent
        response = requests.patch(
            f"{FIREBASE_URL}/businesses/{business_id}.json",
            json={"email_sent": True}
        )
        if response.status_code == 200:
            print(f"Successfully marked email as sent for business {business_id}")
            return True
        else:
            print(f"Error marking email as sent: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error updating Firebase: {e}")
        return False

def test_single_email():
    """Test sending an email to a single business and updating the database."""
    # Initialize Gmail service
    gmail_service = GmailService()
    
    # Get a test business
    business_id, business_data = get_test_business()
    if not business_id or not business_data:
        print("No suitable test business found")
        return
    
    print(f"\nTesting email sending to: {business_data['email']}")
    
    try:
        # Send the email
        success = gmail_service.send_personalized_email(business_data['email'])
        
        if success:
            # Mark email as sent in Firebase
            if mark_email_sent(business_id):
                print(f"✅ Test successful! Email sent and database updated for {business_data['name']}")
            else:
                print(f"❌ Test failed: Email sent but database update failed for {business_data['name']}")
        else:
            print(f"❌ Test failed: Failed to send email to {business_data['email']}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_single_email() 