#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from mailgun_service import MailgunService

# Load environment variables
load_dotenv(override=True)

def test_send_email():
    """Test sending an email to a single business."""
    # Initialize Mailgun service
    mailgun_service = MailgunService()
    
    # Test data
    test_data = {
        'name': 'Test Business',
        'email': 'grossman.stuart1@gmail.com'
    }
    
    print(f"\nTesting email sending to: {test_data['email']}")
    
    # Send the email
    success = mailgun_service.send_personalized_email(test_data['email'], test_data)
    
    if success:
        print(f"Successfully sent email to {test_data['email']}")
        print("✅ Test successful!")
    else:
        print("❌ Test failed: Could not send email")

if __name__ == "__main__":
    test_send_email() 