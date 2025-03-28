# Email Sender Project

A Python-based system for scraping business information and sending personalized emails.

## Project Structure
```
emailSender/
├── src/                    # Source code directory
│   ├── scrapers/          # Web scraping modules
│   │   ├── __init__.py
│   │   ├── business_scraper_parallel.py  # Main parallel business scraper
│   │   └── business_scraper.py           # Base business scraper
│   ├── services/          # External service integrations
│   │   ├── __init__.py
│   │   ├── gmail_service.py             # Gmail API integration
│   │   ├── mailgun_service.py           # Mailgun API integration
│   │   └── hunter_service.py            # Hunter.io API integration
│   ├── utils/            # Utility functions
│   │   ├── __init__.py
│   │   └── email_validator.py           # Email validation utilities
│   ├── config/           # Configuration files
│   │   ├── __init__.py
│   │   └── config.py                    # Main configuration settings
│   └── models/           # Data models and templates
│       ├── __init__.py
│       └── email_templates.py           # Email template definitions
├── tests/                # Test files
│   ├── __init__.py
│   ├── test_scraper.py   # Scraper tests
│   └── test_validator.py # Data validation tests
├── testData/            # Test data storage
├── .env                 # Environment variables
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## File Descriptions

### Scrapers
- `business_scraper_parallel.py`: Main parallel scraper that processes multiple cities and business types concurrently using Grok API
- `business_scraper.py`: Base scraper with core functionality for business data extraction and validation

### Services
- `gmail_service.py`: Handles Gmail API integration for sending emails
- `mailgun_service.py`: Manages email sending through Mailgun API
- `hunter_service.py`: Integrates with Hunter.io API for email finding

### Utils
- `email_validator.py`: Contains functions for email validation, including format checking and DNS validation

### Config
- `config.py`: Central configuration file containing settings for API keys, rate limits, and other parameters

### Models
- `email_templates.py`: Defines email templates and personalization logic

### Tests
- `test_scraper.py`: Tests for the business scraper functionality
- `test_validator.py`: Tests for data validation utilities

## Features

### 1. Business Information Scraping
- Parallel processing of business data
- Multiple validation methods for emails, websites, and phone numbers
- Efficient email scraping with prioritized checks
- DNS validation for email domains

### 2. Email Validation
- Format validation
- DNS record checking
- MX record verification
- Disposable email filtering
- Spam domain detection

### 3. Data Storage
- Firebase integration for storing business data
- JSON-based test data storage
- Validation results logging

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
GROK_API_KEY=your_grok_api_key
FIREBASE_URL=your_firebase_url
```

3. Run tests:
```bash
python3 -m pytest tests/
```

## Usage

### Running the Scraper
```bash
python3 src/scrapers/business_scraper_parallel.py
```

### Validating Data
```bash
python3 tests/test_validator.py
```

## Development History

1. Initial Setup
   - Basic project structure
   - Environment configuration
   - Dependency management

2. Core Scraping Implementation
   - Business data scraping
   - Email validation
   - Website validation
   - Phone number validation

3. Parallel Processing
   - Multi-threaded scraping
   - Rate limiting
   - Error handling

4. Data Validation
   - Comprehensive validation suite
   - Test data generation
   - Results logging

5. Optimization
   - Email validation improvements
   - Scraping efficiency
   - Cost-effective processing

## Testing

The project includes comprehensive tests for:
- Email validation
- Website validation
- Phone number validation
- Data integrity
- Scraping functionality

Run tests with:
```bash
python3 -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 