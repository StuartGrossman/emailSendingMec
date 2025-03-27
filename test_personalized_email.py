#!/usr/bin/env python3

from gmail_service import GmailService

def main():
    # Initialize Gmail service
    gmail_service = GmailService()
    
    # Get a random site ID
    site_id = gmail_service.get_random_site()
    if not site_id:
        print("Failed to get a random site. Please check if there are any sites in the database.")
        return
    
    # Send personalized email about the random site
    result = gmail_service.send_personalized_email(site_id)
    
    if result:
        print("Successfully sent personalized email!")
    else:
        print("Failed to send personalized email. Please check the logs for details.")

if __name__ == "__main__":
    main() 