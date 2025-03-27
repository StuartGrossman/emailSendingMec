from gmail_service import GmailService
from gmail_config import EMAIL_CONFIG
import json

def test_get_random_site():
    print("\n=== Testing get_random_site() ===")
    service = GmailService()
    site_data = service.get_random_site()
    if site_data:
        print("✓ get_random_site() successful")
        print(f"Site data: {json.dumps(site_data, indent=2)}")
    else:
        print("✗ get_random_site() failed")

def test_generate_personalized_email():
    print("\n=== Testing generate_personalized_email() ===")
    service = GmailService()
    # Get a random site first
    site_data = service.get_random_site()
    if not site_data:
        print("✗ Failed to get site data for testing")
        return
    
    email_content = service.generate_personalized_email(site_data)
    if email_content:
        print("✓ generate_personalized_email() successful")
        print("Email content:")
        print(email_content)
    else:
        print("✗ generate_personalized_email() failed")

def test_send_message():
    print("\n=== Testing send_message() ===")
    service = GmailService()
    test_subject = "Test Email"
    test_content = "This is a test email to verify the send_message() function."
    result = service.send_message(EMAIL_CONFIG['test_recipient'], test_subject, test_content)
    if result:
        print("✓ send_message() successful")
        print(f"Message ID: {result.get('id')}")
    else:
        print("✗ send_message() failed")

def test_send_personalized_email():
    print("\n=== Testing send_personalized_email() ===")
    service = GmailService()
    result = service.send_personalized_email()
    if result:
        print("✓ send_personalized_email() successful")
        print(f"Message ID: {result.get('id')}")
    else:
        print("✗ send_personalized_email() failed")

if __name__ == "__main__":
    print("Starting individual function tests...")
    
    # Test each function
    test_get_random_site()
    test_generate_personalized_email()
    test_send_message()
    test_send_personalized_email() 