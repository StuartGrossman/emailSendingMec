#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import json
import time
from gmail_service import GmailService
from config import FIREBASE_URL
import requests

# Load environment variables before any other imports
load_dotenv(override=True)

def get_all_businesses():
    """Get all businesses from Firebase that haven't received an email yet."""
    try:
        response = requests.get(f"{FIREBASE_URL}/businesses.json")
        if response.status_code == 200:
            businesses = response.json()
            if businesses:
                # Filter out businesses that have already received an email
                unsent_businesses = {
                    business_id: data 
                    for business_id, data in businesses.items() 
                    if not data.get('email_sent', False)
                }
                print(f"Found {len(unsent_businesses)} businesses that haven't received an email yet")
                return unsent_businesses
        print(f"Error getting businesses: {response.status_code}")
        return None
    except Exception as e:
        print(f"Error accessing Firebase: {e}")
        return None

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

def send_bulk_emails():
    """Send emails to all businesses that haven't received one yet."""
    # Initialize Gmail service
    gmail_service = GmailService()
    
    # Get all unsent businesses
    businesses = get_all_businesses()
    if not businesses:
        print("No businesses found or error occurred")
        return
    
    # Counter for statistics
    total_businesses = len(businesses)
    successful_sends = 0
    failed_sends = 0
    
    print(f"\nStarting to send emails to {total_businesses} businesses...")
    
    # Process each business
    for business_id, business_data in businesses.items():
        try:
            print(f"\nProcessing business: {business_data['name']} ({business_data['city']}, {business_data['state']})")
            
            # Send the email
            success = gmail_service.send_personalized_email(business_data['email'])
            
            if success:
                # Mark email as sent in Firebase
                if mark_email_sent(business_id):
                    successful_sends += 1
                    print(f"Successfully sent email to {business_data['email']}")
                else:
                    failed_sends += 1
                    print(f"Failed to mark email as sent for {business_data['email']}")
            else:
                failed_sends += 1
                print(f"Failed to send email to {business_data['email']}")
            
            # Add a delay between sends to avoid rate limits
            time.sleep(2)
            
        except Exception as e:
            failed_sends += 1
            print(f"Error processing business {business_id}: {e}")
            continue
    
    # Print summary
    print("\nEmail sending complete!")
    print(f"Total businesses processed: {total_businesses}")
    print(f"Successfully sent: {successful_sends}")
    print(f"Failed to send: {failed_sends}")
    print(f"Success rate: {(successful_sends/total_businesses)*100:.2f}%")

if __name__ == "__main__":
    send_bulk_emails() 