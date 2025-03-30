# Email Sender and Lead Management System

A comprehensive system for sending personalized emails and managing business leads, featuring AI-powered lead analysis and a modern React frontend.

## Features

### 1. Email Sending System
- Personalized email generation using Grok AI
- Support for both Gmail and Mailgun
- Bulk email sending with rate limiting
- Email validation and testing
- Progress tracking and error handling

### 2. Phone Lead Scraper
- AI-powered business analysis using Grok
- Intelligent lead scoring based on multiple factors:
  - Current technology stack
  - Business operations
  - Growth potential
  - Custom software opportunities
  - Decision maker accessibility
- Detailed sales conversation guides
- Firebase integration for lead storage

### 3. React Frontend
- Modern, responsive UI for lead management
- Real-time Firebase integration
- Lead analysis visualization
- Call notes and follow-up tracking
- Lead status management

## Project Structure

```
emailSender/
├── src/
│   ├── components/          # React components
│   │   ├── LeadsList.jsx   # Main leads management interface
│   │   └── LeadCard.jsx    # Individual lead display and notes
│   ├── services/           # Backend services
│   │   ├── gmail_service.py
│   │   ├── mailgun_service.py
│   │   └── phone_lead_scraper.py
│   ├── config/            # Configuration files
│   │   └── config.py
│   └── utils/             # Utility functions
├── tests/                 # Test files
│   ├── test_email.py
│   ├── test_bulk_email.py
│   └── test_phone_lead_scraper.py
└── frontend/             # React frontend
    ├── src/
    │   ├── components/
    │   ├── services/
    │   └── App.jsx
    └── package.json
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/StuartGrossman/emailSendingMec.git
cd emailSendingMec
```

2. Set up Python environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. Set up React frontend:
```bash
cd frontend
npm install
```

## Running Tests

1. Python tests:
```bash
python -m pytest tests/ -v
```

2. React tests:
```bash
cd frontend
npm test
```

## Usage

### Phone Lead Scraper

1. Run the scraper:
```bash
python -m src.services.phone_lead_scraper --city "San Francisco" --state "CA" --business-type "auto_repair"
```

2. View leads in the React frontend:
```bash
cd frontend
npm start
```

### Email Sender

1. Send test email:
```bash
python -m src.services.send_email --to "test@example.com" --subject "Test Email"
```

2. Send bulk emails:
```bash
python -m src.services.send_bulk_emails --city "San Francisco" --state "CA" --business-type "auto_repair"
```

## Environment Variables

Required environment variables:
- `GROK_API_KEY`: Your Grok API key
- `FIREBASE_URL`: Your Firebase Realtime Database URL
- `MAILGUN_API_KEY`: Your Mailgun API key
- `MAILGUN_DOMAIN`: Your Mailgun domain
- `GMAIL_CREDENTIALS`: Path to your Gmail credentials file

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 