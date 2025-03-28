#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import json
import time
from mailgun_service import MailgunService
import requests

# Load environment variables before any other imports
load_dotenv(override=True)

# Get Firebase URL directly from environment
FIREBASE_URL = os.environ.get('FIREBASE_URL')
if not FIREBASE_URL:
    raise ValueError("FIREBASE_URL environment variable is not set")

def get_all_businesses():
    """Get all businesses from Firebase that haven't received an email yet."""
    try:
        # Get the Firebase URL from environment variables
        firebase_url = os.getenv('FIREBASE_URL')
        if not firebase_url:
            raise ValueError("FIREBASE_URL environment variable is not set")
            
        print(f"Using Firebase URL: {firebase_url}")
        print("Fetching businesses from Firebase...")
        
        # Make the request to Firebase
        response = requests.get(f"{firebase_url}/.json")
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            data = response.json()
            if not data:
                print("No data found in Firebase")
                return {}
                
            unsent_businesses = {}
            
            # Iterate through each business type
            for business_type, businesses in data.items():
                # Skip if businesses is None
                if not businesses:
                    continue
                    
                # Iterate through each business in the type
                for business_id, business_data in businesses.items():
                    # Skip if business_data is None
                    if not business_data:
                        continue
                        
                    # Check if the business has an email field and hasn't received an email yet
                    if 'email' in business_data and ('email_sent' not in business_data or not business_data['email_sent']):
                        # Add the business ID to the data for reference
                        business_data['business_id'] = business_id
                        unsent_businesses[business_id] = business_data
                        
            print(f"Found {len(unsent_businesses)} businesses that haven't received an email yet")
            return unsent_businesses
        else:
            print(f"Error getting businesses: {response.status_code}")
            print(f"Response content: {response.text}")
            return {}
            
    except Exception as e:
        print(f"Error in get_all_businesses: {str(e)}")
        return {}

def mark_email_sent(business_id):
    """Mark a business as having received an email in Firebase."""
    try:
        # Get the Firebase URL from environment variables
        firebase_url = os.getenv('FIREBASE_URL')
        if not firebase_url:
            raise ValueError("FIREBASE_URL environment variable is not set")
            
        print(f"Marking email as sent for business: {business_id}")
        
        # Extract business type from the business_id
        # Format is: business_type_city_business_name
        parts = business_id.split('_')
        if len(parts) < 3:
            print(f"Invalid business ID format: {business_id}")
            return False
            
        business_type = parts[0]
        
        # Update the Firebase record
        update_url = f"{firebase_url}/{business_type}/{business_id}.json"
        print(f"Updating Firebase at: {update_url}")
        
        data = {"email_sent": True}
        response = requests.patch(update_url, json=data)
        
        print(f"Update response status: {response.status_code}")
        print(f"Update response content: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error marking email as sent: {str(e)}")
        return False

def send_bulk_emails():
    """Send emails to all businesses that haven't received one yet."""
    mailgun_service = MailgunService()
    businesses = get_all_businesses()
    
    if not businesses:
        print("No businesses found or error occurred")
        return
    
    print(f"Starting to send emails to {len(businesses)} businesses")
    
    for business_id, business_data in businesses.items():
        try:
            # Extract business type and location from the ID
            business_type = business_id.split('_')[0].replace('_', ' ').title()
            
            # Send email to the business
            success = mailgun_service.send_email(
                to_email=business_data['email'],
                subject=f"Custom Software Solutions for {business_data['name']}",
                html_content=f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                        .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; }}
                        .content {{ padding: 20px; }}
                        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Custom Software Solutions for {business_data['name']}</h1>
                        </div>
                        <div class="content">
                            <p>Dear {business_data['name']} team,</p>
                            <p>I hope this email finds you well. I'm reaching out to discuss how we can help streamline your operations and enhance your {business_type} business through custom software solutions.</p>
                            <p>Based on your business profile, I believe we can offer valuable solutions in:</p>
                            <ul>
                                <li>Custom software development</li>
                                <li>Business process automation</li>
                                <li>Integration with existing systems</li>
                                <li>Mobile app development</li>
                            </ul>
                            <p>Would you be interested in a brief conversation about how we can help your business grow?</p>
                            <p>Best regards,<br>Stuart C Grossman<br>Phone: (917) 375-2539</p>
                        </div>
                        <div class="footer">
                            <p>This email was sent to {business_data['email']}. To unsubscribe, please reply with "unsubscribe" in the subject line.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            )
            
            if success:
                # Mark the email as sent in Firebase
                mark_email_sent(business_id)
                print(f"Successfully sent email to {business_data['email']}")
            else:
                print(f"Failed to send email to {business_data['email']}")
            
            # Add a delay between sends to avoid rate limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing business {business_id}: {e}")
            continue

if __name__ == "__main__":
    send_bulk_emails() 