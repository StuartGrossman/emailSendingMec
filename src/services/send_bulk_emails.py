#!/usr/bin/env python3
import json
import os
import time
from datetime import datetime
from typing import List, Dict
from src.services.mailgun_service import MailgunService
from src.config.config import FIREBASE_URL, RATE_LIMIT_DELAY
from src.models.email_templates import match_business_to_template

class BulkEmailSender:
    def __init__(self):
        self.mailgun_service = MailgunService()
        self.sent_emails_file = 'sent_emails.json'
        self.sent_emails = self.load_sent_emails()
        
    def load_sent_emails(self) -> List[str]:
        """Load list of emails that have already been sent."""
        if os.path.exists(self.sent_emails_file):
            with open(self.sent_emails_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_sent_emails(self):
        """Save list of sent emails."""
        with open(self.sent_emails_file, 'w') as f:
            json.dump(self.sent_emails, f)
    
    def get_businesses_from_firebase(self) -> List[Dict]:
        """Get businesses from Firebase that haven't been emailed yet."""
        # TODO: Implement Firebase query to get businesses
        # For now, we'll use test data
        test_data_file = 'testData/scraped_businesses_20240328_123456.json'
        if not os.path.exists(test_data_file):
            print(f"Test data file not found: {test_data_file}")
            return []
            
        with open(test_data_file, 'r') as f:
            businesses = json.load(f)
            
        # Filter out businesses that have already been emailed
        return [b for b in businesses if b.get('email') not in self.sent_emails]
    
    def send_bulk_emails(self, delay: int = 60):
        """Send personalized emails to all businesses with a delay between each."""
        businesses = self.get_businesses_from_firebase()
        if not businesses:
            print("No businesses found to email")
            return
            
        print(f"Found {len(businesses)} businesses to email")
        
        for business in businesses:
            email = business.get('email')
            if not email or email in self.sent_emails:
                continue
                
            print(f"\nSending email to {business['name']} ({email})")
            
            # Send personalized email
            success = self.mailgun_service.send_personalized_email(email, business)
            
            if success:
                print(f"Successfully sent email to {email}")
                self.sent_emails.append(email)
                self.save_sent_emails()
            else:
                print(f"Failed to send email to {email}")
            
            # Add delay between emails
            print(f"Waiting {delay} seconds before next email...")
            time.sleep(delay)
        
        print("\nBulk email sending completed!")
        print(f"Total emails sent: {len(self.sent_emails)}")

def main():
    sender = BulkEmailSender()
    sender.send_bulk_emails()

if __name__ == "__main__":
    main() 