#!/usr/bin/env python3
import pytest
from src.services.send_bulk_emails import BulkEmailSender
from src.services.mailgun_service import MailgunService

def test_bulk_email_sender_initialization():
    """Test that BulkEmailSender initializes correctly."""
    sender = BulkEmailSender()
    assert sender.mailgun_service is not None
    assert isinstance(sender.sent_emails, list)
    assert sender.sent_emails_file == 'sent_emails.json'

def test_load_sent_emails():
    """Test loading sent emails from file."""
    sender = BulkEmailSender()
    emails = sender.load_sent_emails()
    assert isinstance(emails, list)

def test_save_sent_emails():
    """Test saving sent emails to file."""
    sender = BulkEmailSender()
    test_emails = ['test1@example.com', 'test2@example.com']
    sender.sent_emails = test_emails
    sender.save_sent_emails()
    
    # Create a new instance to verify persistence
    new_sender = BulkEmailSender()
    loaded_emails = new_sender.load_sent_emails()
    assert loaded_emails == test_emails

def test_get_businesses_from_firebase():
    """Test getting businesses from Firebase."""
    sender = BulkEmailSender()
    businesses = sender.get_businesses_from_firebase()
    assert isinstance(businesses, list)

def test_send_bulk_emails():
    """Test sending bulk emails."""
    sender = BulkEmailSender()
    # This will use the test data file
    sender.send_bulk_emails(delay=1)  # Use 1 second delay for testing
    assert len(sender.sent_emails) > 0

def test_mailgun_service():
    """Test Mailgun service functionality."""
    service = MailgunService()
    assert service.api_key is not None
    assert service.domain is not None
    assert service.base_url is not None
    assert service.auth is not None

if __name__ == "__main__":
    pytest.main([__file__, '-v']) 