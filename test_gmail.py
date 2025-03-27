#!/usr/bin/env python3

from gmail_service import GmailService

def main():
    # Initialize Gmail service
    gmail_service = GmailService()
    
    # Test the connection
    print("Testing Gmail API connection...")
    result = gmail_service.test_connection()
    
    if result:
        print("Successfully sent test email!")
    else:
        print("Failed to send test email. Please check your credentials and try again.")

if __name__ == "__main__":
    main() 