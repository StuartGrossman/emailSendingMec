#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API Configuration
GMAIL_CONFIG = {
    "web": {
        "client_id": os.getenv("GMAIL_CLIENT_ID"),
        "project_id": os.getenv("GMAIL_PROJECT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.getenv("GMAIL_CLIENT_SECRET")
    }
}

# Email Configuration
EMAIL_CONFIG = {
    "sender_email": os.getenv("SENDER_EMAIL"),
    "test_recipient": os.getenv("TEST_RECIPIENT"),
    "scopes": [
        "https://mail.google.com/",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/gmail.send"
    ]
}

# Template Configuration
TEMPLATE_CONFIG = {
    "max_tokens": 1000,
    "temperature": 0.7,
    "top_p": 0.9
} 