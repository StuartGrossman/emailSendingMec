#!/usr/bin/env python3

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Grok API Configuration
GROK_API_KEY = os.environ.get('GROK_API_KEY')
GROK_API_KEY_2 = os.environ.get('GROK_API_KEY_2')
GROK_API_KEY_3 = os.environ.get('GROK_API_KEY_3')
GROK_API_KEY_4 = os.environ.get('GROK_API_KEY_4')

# Firebase Configuration
FIREBASE_URL = os.environ.get('FIREBASE_URL')
FIREBASE_CREDENTIALS = {
    "type": "service_account",
    "project_id": os.environ.get('FIREBASE_PROJECT_ID'),
    "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": os.environ.get('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
    "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
    "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
    "auth_uri": os.environ.get('FIREBASE_AUTH_URI'),
    "token_uri": os.environ.get('FIREBASE_TOKEN_URI'),
    "auth_provider_x509_cert_url": os.environ.get('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
    "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_X509_CERT_URL')
}

# Mailgun Configuration
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
TEST_RECIPIENT = os.environ.get('TEST_RECIPIENT')

# Hunter.io Configuration
HUNTER_API_KEY = os.environ.get('HUNTER_API_KEY')

# API Keys for Grok
GROK_API_KEYS = [
    "xai-S375bT9UgdT3qzjhXHO88F3WHbmGgZzlzJMbw05d9Bkv3s6cGwZcM3fff40fb7j8gi9xgLpmnrgSurmE",
    "xai-TiuZX0EVps11iHwd1zp6GBN3xA8gip3nHQKDdtu2xA2KQ1XmNQuPLJv5E0DpIRWyqalYBfNkB3O4mmQ0",
    "xai-D1BJ6k1eIjUOMhz1huMsZWugFkJZXkXSxBy2ZdEY5NjS6NaF3WTP8Z52vV91qgXoZ7nyAeZUnjgwyF3e",
    "xai-tSqllE2zOWUdhDaDfY0SILvJ1wHC02Oqt0mSMDdAfsugQOcRVURjntYL2nm2pxJBLUI7xeP0lmT7a5au"
]

# Number of parallel processes
NUM_PROCESSES = 4

# Rate limiting settings
RATE_LIMIT_DELAY = 2  # seconds between requests
MAX_RETRIES = 3

# Timeout settings
REQUEST_TIMEOUT = 30  # seconds

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = "scraper.log"

# Google Places API Configuration
GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY', 'google_places_api_key')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'deepseek_api_key')
MIN_RATING = 4.0  # Minimum Google rating to consider
MIN_REVIEWS = 50  # Minimum number of reviews to consider 