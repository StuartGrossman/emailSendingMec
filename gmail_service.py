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
from gmail_config import GMAIL_CONFIG, EMAIL_CONFIG
import requests
import json
from datetime import datetime
from config import FIREBASE_URL
from grok_service import GrokService

class GmailService:
    def __init__(self):
        self.creds = None
        self.service = None
        self.firebase_url = FIREBASE_URL
        self.grok_service = GrokService()
        self._authenticate()

    def _get_sites_from_firebase(self):
        """Get sites from Firebase Realtime Database."""
        try:
            # Get sites from the businesses endpoint
            response = requests.get(f"{self.firebase_url}/businesses.json")
            if response.status_code == 200:
                sites = response.json()
                if sites:
                    print(f"Found {len(sites)} sites in the database")
                    return sites
            print(f"Error getting sites: {response.status_code}")
            return None
        except Exception as e:
            print(f"Error accessing Firebase: {e}")
            return None

    def get_random_site(self):
        """Get a random site from Firebase."""
        try:
            sites = self._get_sites_from_firebase()
            if not sites:
                print("No sites found in the database")
                return None
            
            # Convert dictionary to list of tuples (id, data)
            sites_list = [(site_id, data) for site_id, data in sites.items()]
            if not sites_list:
                print("No sites available")
                return None
            
            # Choose a random site
            random_site_id, site_data = random.choice(sites_list)
            print(f"Selected random site: {random_site_id}")
            print(f"Site data: {json.dumps(site_data, indent=2)}")
            
            # Ensure site data is a dictionary
            if not isinstance(site_data, dict):
                print("Invalid site data format")
                return None
                
            return site_data
            
        except Exception as e:
            print(f"Error getting random site: {e}")
            return None

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        print("Starting authentication process...")
        
        if os.path.exists('token.json'):
            print("Found existing token, attempting to use it...")
            self.creds = Credentials.from_authorized_user_file('token.json', EMAIL_CONFIG['scopes'])
        
        if not self.creds or not self.creds.valid:
            print("No valid credentials found, starting new authentication flow...")
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("Refreshing expired credentials...")
                self.creds.refresh(Request())
            else:
                print("Starting new OAuth flow...")
                flow = InstalledAppFlow.from_client_config(GMAIL_CONFIG, EMAIL_CONFIG['scopes'])
                print("Please authorize the application in your browser...")
                self.creds = flow.run_local_server(port=8080)
                print("Authorization successful!")
            
            print("Saving credentials for future use...")
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        print("Building Gmail service...")
        self.service = build('gmail', 'v1', credentials=self.creds)
        print("Authentication complete!")

    def create_message(self, to, subject, message_text):
        """Create a message for an email."""
        sender_email = os.environ.get('SENDER_EMAIL', '').strip()
        print(f"DEBUG: Creating message with to={to}, from={sender_email}")
        
        message = MIMEMultipart('alternative')
        message['to'] = to.strip()
        message['from'] = sender_email
        message['subject'] = subject
        
        # Add Gmail-specific headers
        message['X-Priority'] = '1'
        message['X-MSMail-Priority'] = 'High'
        message['Importance'] = 'high'
        message['Content-Type'] = 'text/html; charset=utf-8'
        message['MIME-Version'] = '1.0'
        
        # Add spam prevention headers
        message['List-Unsubscribe'] = f'<mailto:{sender_email}?subject=unsubscribe>'
        message['Precedence'] = 'bulk'
        message['X-Auto-Response-Suppress'] = 'OOF, AutoReply'
        message['X-Entity-Ref-ID'] = 'new'
        message['X-Report-Abuse'] = f'Please report abuse to {sender_email}'
        
        # Add Gmail delegation headers
        message['X-Google-Sender-Delegation'] = 'true'
        message['X-Gm-Message-State'] = 'DELEGATED'
        
        # Add SPF and DKIM headers
        message['X-Sender'] = sender_email
        message['X-Originating-IP'] = '[127.0.0.1]'
        message['X-Google-Original-Auth'] = 'true'
        
        # Create both plain text and HTML versions
        text_part = MIMEText(message_text, 'plain')
        html_part = MIMEText(message_text, 'html')
        
        # Add both parts to the message
        message.attach(text_part)
        message.attach(html_part)
        
        print(f"DEBUG: Final message headers: {dict(message.items())}")
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}

    def send_message(self, to, subject, message_text):
        """Send an email message."""
        try:
            print(f"Creating message to {to}...")
            message = self.create_message(to, subject, message_text)
            print("Sending message...")
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            print(f'Message sent successfully! Message Id: {sent_message["id"]}')
            return sent_message
        except Exception as e:
            print(f'An error occurred while sending the message: {e}')
            return None

    def generate_personalized_email(self, site_data):
        """Generate personalized email content using site data and Grok."""
        try:
            # Extract information from site data
            name = site_data.get('name', 'Valued Business')
            description = site_data.get('description', 'you provide valuable services to your customers')
            website = site_data.get('website', 'N/A')
            tech_analysis = site_data.get('technical_analysis', {})
            business_analysis = site_data.get('business_analysis', {})
            sender_email = os.environ.get('SENDER_EMAIL', '').strip()
            
            # Create a prompt for Grok
            prompt = f"""Create a professional sales email for {name}, a business that {description.lower()}.

The email should:
1. Start with a personal introduction about Stuart Grossman
2. Be personalized and engaging
3. Focus on creative software solutions leveraging the latest technology
4. Highlight rapid development capabilities using modern frameworks
5. Suggest specific improvements based on their current technology stack
6. Include concrete examples of similar solutions we've built
7. Emphasize quick deployment and fast ROI
8. End with a call to action asking them to reply to schedule a call
9. Be formatted in HTML with modern styling
10. Use a professional yet innovative tone
11. Include their website: {website}
12. Include my phone number: (415) 999-4541

Format the response as HTML with CSS styling similar to this template:
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            max-width: 650px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8fafc;
        }}
        .container {{
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            padding: 32px;
            margin-bottom: 24px;
        }}
        .header {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 24px;
            border: 1px solid rgba(147, 197, 253, 0.2);
        }}
        .business-name {{
            color: #0f172a;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 16px;
            letter-spacing: -0.025em;
        }}
        .section {{
            background: #ffffff;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid #e2e8f0;
            transition: transform 0.2s ease-in-out;
        }}
        .section:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.1);
        }}
        .section-title {{
            color: #0f172a;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .section-title::before {{
            content: "";
            display: inline-block;
            width: 4px;
            height: 20px;
            background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%);
            border-radius: 2px;
            margin-right: 8px;
        }}
        .bullet-points {{
            list-style-type: none;
            padding-left: 0;
            margin: 16px 0;
        }}
        .bullet-points li {{
            margin-bottom: 12px;
            padding-left: 28px;
            position: relative;
        }}
        .bullet-points li::before {{
            content: "→";
            color: #3b82f6;
            position: absolute;
            left: 0;
            font-weight: 600;
        }}
        .tech-highlight {{
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
            border: 1px solid #e2e8f0;
        }}
        .cta-section {{
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border-radius: 12px;
            padding: 24px;
            margin-top: 32px;
            text-align: center;
            border: 1px solid rgba(147, 197, 253, 0.3);
        }}
        .cta-text {{
            font-size: 18px;
            font-weight: 600;
            color: #1e40af;
            margin-bottom: 16px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid #e2e8f0;
            font-size: 14px;
            color: #64748b;
            text-align: center;
        }}
        .highlight {{
            color: #2563eb;
            font-weight: 600;
        }}
        a {{
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s ease-in-out;
        }}
        a:hover {{
            color: #1d4ed8;
            text-decoration: underline;
        }}
        .intro-text {{
            font-size: 16px;
            line-height: 1.8;
            color: #334155;
            margin-bottom: 24px;
        }}
        .contact-info {{
            background: #f8fafc;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="business-name">Dear {name} Team,</div>
            <p class="intro-text">Hi, my name is Stuart Grossman, and I'm a software engineer with over 10 years of experience building full-stack applications. Recent advances in LLM and AI technologies have made it possible for independent developers like myself to deliver powerful, custom software solutions at a fraction of the cost and time it once required.</p>
            <p class="intro-text">Just a couple of years ago, developing custom web technologies meant huge costs, long development cycles, and uncertainty about the final product. Today, a single skilled developer or a small, agile team can create high-impact software for your business in days, not months—at a reasonable rate.</p>
            <p class="intro-text">If you've had software ideas but dismissed them as too expensive, complex, or time-consuming, now is the perfect time to reconsider. I specialize in helping businesses streamline operations, reduce overhead, and automate complex tasks across platforms.</p>
        </div>

        <div class="section">
            <div class="section-title">Innovative AI-Powered Solutions</div>
            <div class="tech-highlight">
                We specialize in creating custom web applications that leverage:
                <ul class="bullet-points">
                    <li>Advanced LLM-powered automation for customer service and operations</li>
                    <li>Seamless API integrations with your existing systems</li>
                    <li>Intelligent web scraping for market research and competitor analysis</li>
                    <li>Automated marketing campaigns with personalized content generation</li>
                    <li>Real-time data analytics and business intelligence dashboards</li>
                </ul>
            </div>
            <p>Our solutions are built using the latest technology stack, ensuring rapid development and deployment. We can typically deliver a production-ready MVP within 2-4 weeks.</p>
        </div>

        <div class="section">
            <div class="section-title">Rapid Development & Deployment</div>
            <p>We use modern frameworks and tools that enable us to:</p>
            <ul class="bullet-points">
                <li>Develop and deploy features in days, not weeks</li>
                <li>Scale your application automatically as your business grows</li>
                <li>Maintain high performance and security standards</li>
                <li>Provide real-time monitoring and analytics</li>
            </ul>
        </div>

        <div class="cta-section">
            <p class="cta-text">Let's Build Something Amazing Together</p>
            <p>A quick call is all it takes to explore how we can optimize your business with cutting-edge technology. Let's build something that saves you time, increases efficiency, and keeps you ahead of the competition.</p>
            <p>Simply reply to this email or call me at (415) 999-4541 to schedule a call where we can discuss your specific needs.</p>
        </div>

        <div class="contact-info">
            <p><strong>Contact Information:</strong></p>
            <p>📧 Email: {sender_email}</p>
            <p>📱 Phone: (415) 999-4541</p>
        </div>

        <div class="footer">
            <p>Looking forward to connecting!<br><span class="highlight">Stuart Grossman</span></p>
        </div>
    </div>
</body>
</html>"""

            # Generate email content using Grok
            email_content = self.grok_service.generate_email_content(prompt)
            
            if not email_content:
                # Fallback to template if Grok fails
                print("Grok generation failed, using template fallback")
                email_content = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            max-width: 650px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8fafc;
        }}
        .container {{
            background: #ffffff;
            border-radius: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            padding: 32px;
            margin-bottom: 24px;
        }}
        .header {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 24px;
            border: 1px solid rgba(147, 197, 253, 0.2);
        }}
        .business-name {{
            color: #0f172a;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 16px;
            letter-spacing: -0.025em;
        }}
        .section {{
            background: #ffffff;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid #e2e8f0;
            transition: transform 0.2s ease-in-out;
        }}
        .section:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.1);
        }}
        .section-title {{
            color: #0f172a;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .section-title::before {{
            content: "";
            display: inline-block;
            width: 4px;
            height: 20px;
            background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%);
            border-radius: 2px;
            margin-right: 8px;
        }}
        .bullet-points {{
            list-style-type: none;
            padding-left: 0;
            margin: 16px 0;
        }}
        .bullet-points li {{
            margin-bottom: 12px;
            padding-left: 28px;
            position: relative;
        }}
        .bullet-points li::before {{
            content: "→";
            color: #3b82f6;
            position: absolute;
            left: 0;
            font-weight: 600;
        }}
        .tech-highlight {{
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
            border: 1px solid #e2e8f0;
        }}
        .cta-section {{
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border-radius: 12px;
            padding: 24px;
            margin-top: 32px;
            text-align: center;
            border: 1px solid rgba(147, 197, 253, 0.3);
        }}
        .cta-text {{
            font-size: 18px;
            font-weight: 600;
            color: #1e40af;
            margin-bottom: 16px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 24px;
            border-top: 1px solid #e2e8f0;
            font-size: 14px;
            color: #64748b;
            text-align: center;
        }}
        .highlight {{
            color: #2563eb;
            font-weight: 600;
        }}
        a {{
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s ease-in-out;
        }}
        a:hover {{
            color: #1d4ed8;
            text-decoration: underline;
        }}
        .intro-text {{
            font-size: 16px;
            line-height: 1.8;
            color: #334155;
            margin-bottom: 24px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="business-name">Dear {name} Team,</div>
            <p class="intro-text">Hi, my name is Stuart Grossman, and I'm a software engineer with over 10 years of experience building full-stack applications. Recent advances in LLM and AI technologies have made it possible for independent developers like myself to deliver powerful, custom software solutions at a fraction of the cost and time it once required.</p>
            <p class="intro-text">Just a couple of years ago, developing custom web technologies meant huge costs, long development cycles, and uncertainty about the final product. Today, a single skilled developer or a small, agile team can create high-impact software for your business in days, not months—at a reasonable rate.</p>
            <p class="intro-text">If you've had software ideas but dismissed them as too expensive, complex, or time-consuming, now is the perfect time to reconsider. I specialize in helping businesses streamline operations, reduce overhead, and automate complex tasks across platforms.</p>
        </div>

        <div class="section">
            <div class="section-title">Innovative AI-Powered Solutions</div>
            <div class="tech-highlight">
                We specialize in creating custom web applications that leverage:
                <ul class="bullet-points">
                    <li>Advanced LLM-powered automation for customer service and operations</li>
                    <li>Seamless API integrations with your existing systems</li>
                    <li>Intelligent web scraping for market research and competitor analysis</li>
                    <li>Automated marketing campaigns with personalized content generation</li>
                    <li>Real-time data analytics and business intelligence dashboards</li>
                </ul>
            </div>
            <p>Our solutions are built using the latest technology stack, ensuring rapid development and deployment. We can typically deliver a production-ready MVP within 2-4 weeks.</p>
        </div>

        <div class="section">
            <div class="section-title">Rapid Development & Deployment</div>
            <p>We use modern frameworks and tools that enable us to:</p>
            <ul class="bullet-points">
                <li>Develop and deploy features in days, not weeks</li>
                <li>Scale your application automatically as your business grows</li>
                <li>Maintain high performance and security standards</li>
                <li>Provide real-time monitoring and analytics</li>
            </ul>
        </div>

        <div class="cta-section">
            <p class="cta-text">Let's Build Something Amazing Together</p>
            <p>A quick call is all it takes to explore how we can optimize your business with cutting-edge technology. Let's build something that saves you time, increases efficiency, and keeps you ahead of the competition.</p>
            <p>Simply reply to this email or call me at (415) 999-4541 to schedule a call where we can discuss your specific needs.</p>
        </div>

        <div class="contact-info">
            <p><strong>Contact Information:</strong></p>
            <p>📧 Email: {sender_email}</p>
            <p>📱 Phone: (415) 999-4541</p>
        </div>

        <div class="footer">
            <p>Looking forward to connecting!<br><span class="highlight">Stuart Grossman</span></p>
        </div>
    </div>
</body>
</html>"""
            
            return email_content
        except Exception as e:
            print(f"Error generating email content: {str(e)}")
            print(f"Site data structure: {json.dumps(site_data, indent=2)}")
            return None

    def send_personalized_email(self, recipient_email):
        """Send a personalized email about a specific site."""
        print("\nPreparing personalized email...")
        
        try:
            # Get site data
            site_data = self.get_random_site()
            if not site_data:
                raise ValueError("Failed to get random site data")
            
            # Generate personalized content
            email_content = self.generate_personalized_email(site_data)
            if not email_content:
                raise ValueError("Failed to generate email content")
            
            # Create subject line
            site_name = site_data.get('name', 'Unknown Business')
            subject = f"Custom Software Solutions for {site_name}"
            
            # Send the email
            print(f"Sending email to {recipient_email} about {site_name}...")
            result = self.send_message(recipient_email, subject, email_content)
            if not result:
                raise ValueError("Failed to send email message")
            
            print("Email sent successfully!")
            return result
            
        except Exception as e:
            print(f"Error in send_personalized_email: {str(e)}")
            return None

    def test_connection(self):
        """Test the Gmail API connection by sending a test email."""
        print("\nTesting Gmail API connection...")
        subject = "Gmail API Test - Authenticated Sender"
        message_text = """This is a test email from the Gmail API integration.
        
This email is sent from an authenticated application using the Gmail API.
The sender's identity has been verified through OAuth2 authentication.

Best regards,
EmailSender Application"""
        return self.send_message(EMAIL_CONFIG['test_recipient'], subject, message_text) 