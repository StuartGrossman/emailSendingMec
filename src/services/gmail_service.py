#!/usr/bin/env python3

import os
from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv(override=True)

import base64
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional

class GmailService:
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    TOKEN_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'token.json')
    CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'credentials.json')
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.last_send_time = None
        self.daily_send_count = 0
        self.daily_limit = 500  # Gmail's daily sending limit
        self.min_delay = 2  # Minimum delay between emails in seconds
        self.max_delay = 5  # Maximum delay between emails in seconds
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API."""
        if os.path.exists(self.TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, self.SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_FILE, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(self.TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=self.creds)

    def create_message(self, to: str, subject: str, html_content: str, 
                      from_email: Optional[str] = None) -> Dict:
        """Create a message for an email."""
        message = MIMEMultipart('alternative')
        
        # Set sender
        if from_email:
            message['from'] = from_email
        else:
            message['from'] = 'grossman.stuart1@gmail.com'
            
        message['to'] = to
            message['subject'] = subject
            
        # Add text and HTML parts
        text_part = MIMEText(html_content.replace('<br>', '\n').replace('</p>', '\n'), 'plain')
        html_part = MIMEText(html_content, 'html')
        
        message.attach(text_part)
        message.attach(html_part)
        
        # Add headers to improve deliverability
        message['List-Unsubscribe'] = f'<mailto:{message["from"]}?subject=unsubscribe>'
            message['Precedence'] = 'bulk'
            message['X-Auto-Response-Suppress'] = 'OOF, AutoReply'
            
            return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}
            
    def send_email(self, to: str, subject: str, html_content: str, 
                  from_email: Optional[str] = None) -> bool:
        """Send an email with rate limiting and error handling."""
        try:
            # Check daily limit
            if self.daily_send_count >= self.daily_limit:
                print("Daily sending limit reached")
                return False
                
            # Add random delay between emails
            if self.last_send_time:
                delay = random.uniform(self.min_delay, self.max_delay)
                time.sleep(delay)
                
            # Create and send message
            message = self.create_message(to, subject, html_content, from_email)
            self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            # Update tracking
            self.last_send_time = datetime.now()
            self.daily_send_count += 1
            
            # Reset daily count if it's a new day
            if self.last_send_time.date() < datetime.now().date():
                self.daily_send_count = 0
                
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def test_connection(self):
        """Test the Gmail API connection by sending a test email."""
        print("\nTesting Gmail API connection...")
        subject = "Gmail API Test - Authenticated Sender"
        message_text = """This is a test email from the Gmail API integration.
        
This email is sent from an authenticated application using the Gmail API.
The sender's identity has been verified through OAuth2 authentication.

Best regards,
EmailSender Application"""
        return self.send_email('grossman.stuart1@gmail.com', subject, message_text) 