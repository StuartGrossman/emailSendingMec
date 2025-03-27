#!/usr/bin/env python3

import sys
from gmail_service import GmailService

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 send_email.py <to> <subject> <message>")
        sys.exit(1)

    to_email = sys.argv[1]
    subject = sys.argv[2]
    message = sys.argv[3]

    try:
        # Initialize Gmail service
        gmail_service = GmailService()
        
        # Send the email
        result = gmail_service.send_message(to_email, subject, message)
        
        if result:
            print("Email sent successfully!")
            sys.exit(0)
        else:
            print("Failed to send email")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 