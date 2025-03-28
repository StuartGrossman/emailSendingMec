import os
import requests
from dotenv import load_dotenv
from hunter_service import HunterService

# Load environment variables
load_dotenv()

class MailgunService:
    def __init__(self):
        self.api_key = os.getenv('MAILGUN_API_KEY')
        self.domain = os.getenv('MAILGUN_DOMAIN')
        self.sender_name = os.getenv('SENDER_NAME', 'Stuart Grossman')
        self.sender_email = os.getenv('SENDER_EMAIL', 'grossman.stuart1@gmail.com')
        self.base_url = f"https://api.mailgun.net/v3/{self.domain}"
        self.auth = ("api", self.api_key)
        self.hunter_service = HunterService()

    def send_email(self, to_email, subject, html_content):
        """Send an email using Mailgun API."""
        try:
            # Verify email using Hunter.io
            if not self.hunter_service.verify_email(to_email):
                print(f"Email verification failed for {to_email}")
                return False

            print(f"DEBUG: Using Mailgun domain: {self.domain}")
            print(f"DEBUG: Using API key: {self.api_key[:5]}...")
            
            # Prepare the email data
            data = {
                "from": f"{self.sender_name} <{self.sender_email}>",
                "to": to_email,
                "subject": subject,
                "text": "Congratulations, you just sent an email with Mailgun! You are truly awesome!",
                "html": html_content
            }

            print(f"DEBUG: Sending email with data: {data}")
            
            # Send the email
            response = requests.post(
                f"{self.base_url}/messages",
                auth=self.auth,
                data=data
            )

            print(f"DEBUG: Response status code: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")

            if response.status_code == 200:
                print(f"Email sent successfully to {to_email}")
                return True
            else:
                print(f"Failed to send email: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_personalized_email(self, to_email, business_data=None):
        """Send a personalized email using Mailgun API."""
        try:
            # Verify email using Hunter.io
            if not self.hunter_service.verify_email(to_email):
                print(f"Email verification failed for {to_email}")
                return False

            # Generate email content
            subject = f"Custom Software Solutions for {business_data['name'] if business_data else 'Your Business'}"
            
            # Create HTML content
            html_content = f"""
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
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
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
                    }}
                    .section-title {{
                        color: #0f172a;
                        font-size: 18px;
                        font-weight: 600;
                        margin-bottom: 16px;
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
                    .cta-section {{
                        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
                        border-radius: 12px;
                        padding: 24px;
                        margin-top: 32px;
                        text-align: center;
                        border: 1px solid rgba(147, 197, 253, 0.3);
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
                        <div class="business-name">Dear {business_data['name'] if business_data else 'Business Owner'},</div>
                        <p>Hi, my name is Stuart Grossman, and I'm a software engineer with over 10 years of experience building full-stack applications. Recent advances in LLM and AI technologies have made it possible for independent developers like myself to deliver powerful, custom software solutions at a fraction of the cost and time it once required.</p>
                    </div>

                    <div class="section">
                        <div class="section-title">Innovative AI-Powered Solutions</div>
                        <p>We specialize in creating custom web applications that leverage:</p>
                        <ul class="bullet-points">
                            <li>Advanced LLM-powered automation for customer service and operations</li>
                            <li>Seamless API integrations with your existing systems</li>
                            <li>Intelligent web scraping for market research and competitor analysis</li>
                            <li>Automated marketing campaigns with personalized content generation</li>
                            <li>Real-time data analytics and business intelligence dashboards</li>
                        </ul>
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
                        <p>Let's Build Something Amazing Together</p>
                        <p>A quick call is all it takes to explore how we can optimize your business with cutting-edge technology.</p>
                        <p>Simply reply to this email or call me at (415) 999-4541 to schedule a call where we can discuss your specific needs.</p>
                    </div>

                    <div class="contact-info">
                        <p><strong>Contact Information:</strong></p>
                        <p>📧 Email: grossman.stuart1@gmail.com</p>
                        <p>📱 Phone: (415) 999-4541</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Send the email
            return self.send_email(to_email, subject, html_content)

        except Exception as e:
            print(f"Error sending personalized email: {e}")
            return False 