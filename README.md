# Email Sending Mechanism

A Python-based system for gathering business information and generating personalized email campaigns.

## Features

### Business Scraper
- Randomly selects from 20 major US cities
- Targets 20 different business types
- Includes software need probability scoring (1-10)
- Validates business size and criteria
- Stores data in Firebase Realtime Database

### Email Template System
- Four specialized email templates
- Business-specific matching algorithm
- Personalized content generation
- Firebase integration for email storage

## Setup

1. Clone the repository:
```bash
git clone https://github.com/StuartGrossman/emailSendingMec.git
cd emailSendingMec
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Firebase credentials (if needed)

## Usage

1. Run the business scraper:
```bash
python business_scraper.py
```

2. Generate email templates:
```bash
python email_templates.py
```

## Project Structure

- `business_scraper.py`: Main script for gathering business information
- `email_templates.py`: Email template generation and matching
- `requirements.txt`: Project dependencies
- `README.md`: Project documentation

## Data Structure

### Business Information
- Basic details (name, email, website)
- Location (city, state)
- Business type and software probability
- Technical analysis
- Business analysis

### Email Templates
- General software solutions
- Automation-focused
- Compliance and security
- Niche industry solutions

## License

MIT License 