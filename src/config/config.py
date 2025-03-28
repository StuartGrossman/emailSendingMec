#!/usr/bin/env python3

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Grok API Configuration
GROK_API_KEY = os.environ.get('GROK_API_KEY')

# Firebase Configuration
FIREBASE_URL = os.environ.get('FIREBASE_URL')
FIREBASE_CLIENT_ID = os.environ.get('FIREBASE_CLIENT_ID')
FIREBASE_CLIENT_CERT_URL = os.environ.get('FIREBASE_CLIENT_CERT_URL')
FIREBASE_PRIVATE_KEY_ID = os.environ.get('FIREBASE_PRIVATE_KEY_ID')
FIREBASE_PRIVATE_KEY = os.environ.get('FIREBASE_PRIVATE_KEY')
FIREBASE_CLIENT_EMAIL = os.environ.get('FIREBASE_CLIENT_EMAIL')

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