import requests
from bs4 import BeautifulSoup
import re
from email_validator import validate_email
import time
from typing import Optional, Tuple
import random

def get_random_user_agent():
    """Return a random user agent string."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
    ]
    return random.choice(user_agents)

def get_headers():
    """Return headers that mimic a browser."""
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

def find_valid_email(soup: BeautifulSoup, business_name: str) -> Tuple[Optional[str], str]:
    """
    Search for valid email addresses in the webpage.
    Returns tuple of (email, message) where email is None if no valid email found.
    """
    # Common email patterns to look for
    email_patterns = [
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Standard email
        r'[a-zA-Z0-9._%+-]+\s*\[at\]\s*[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # [at] format
        r'[a-zA-Z0-9._%+-]+\s*\(at\)\s*[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # (at) format
        r'[a-zA-Z0-9._%+-]+\s*@\s*[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'  # Spaced @ format
    ]
    
    # Common email prefixes to look for
    email_prefixes = [
        'email', 'contact', 'info', 'support', 'help', 'inquiries',
        'business', 'office', 'admin', 'sales', 'marketing'
    ]
    
    # First try to find email in meta tags
    meta_tags = soup.find_all('meta')
    for tag in meta_tags:
        content = tag.get('content', '')
        for pattern in email_patterns:
            matches = re.findall(pattern, content)
            for email in matches:
                # Clean up the email
                email = re.sub(r'\s*\[at\]\s*', '@', email)
                email = re.sub(r'\s*\(at\)\s*', '@', email)
                email = re.sub(r'\s*@\s*', '@', email)
                
                # Validate the email
                is_valid, message = validate_email(email)
                if is_valid:
                    return email, "Valid email found in meta tags"
    
    # Look for email in text content
    text_content = soup.get_text()
    for pattern in email_patterns:
        matches = re.findall(pattern, text_content)
        for email in matches:
            # Clean up the email
            email = re.sub(r'\s*\[at\]\s*', '@', email)
            email = re.sub(r'\s*\(at\)\s*', '@', email)
            email = re.sub(r'\s*@\s*', '@', email)
            
            # Validate the email
            is_valid, message = validate_email(email)
            if is_valid:
                return email, "Valid email found in text content"
    
    # Look for email in href attributes
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href', '')
        if href.startswith('mailto:'):
            email = href[7:]  # Remove 'mailto:' prefix
            is_valid, message = validate_email(email)
            if is_valid:
                return email, "Valid email found in mailto link"
    
    # Look for contact forms
    forms = soup.find_all('form')
    for form in forms:
        # Check form action for email
        action = form.get('action', '')
        if 'mailto:' in action:
            email = action.split('mailto:')[1].split('?')[0]
            is_valid, message = validate_email(email)
            if is_valid:
                return email, "Valid email found in form action"
        
        # Check form fields for email hints
        inputs = form.find_all('input')
        for input_field in inputs:
            placeholder = input_field.get('placeholder', '').lower()
            name = input_field.get('name', '').lower()
            if any(prefix in placeholder or prefix in name for prefix in email_prefixes):
                # Look for email in nearby text
                parent = input_field.parent
                if parent:
                    text = parent.get_text()
                    for pattern in email_patterns:
                        matches = re.findall(pattern, text)
                        for email in matches:
                            email = re.sub(r'\s*\[at\]\s*', '@', email)
                            email = re.sub(r'\s*\(at\)\s*', '@', email)
                            email = re.sub(r'\s*@\s*', '@', email)
                            
                            is_valid, message = validate_email(email)
                            if is_valid:
                                return email, "Valid email found near contact form"
    
    return None, "No valid email found on page"

def scrape_business_website(url: str, business_name: str, max_depth: int = 2) -> Tuple[Optional[str], str]:
    """
    Scrape business website for valid email address.
    Returns tuple of (email, message) where email is None if no valid email found.
    """
    try:
        # Add random delay between 2-5 seconds to be respectful to servers
        time.sleep(random.uniform(2, 5))
        
        # Make request with browser-like headers
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        
        # Check if we got HTML content
        if 'text/html' not in response.headers.get('Content-Type', '').lower():
            return None, "Response is not HTML content"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # First try to find email on main page
        email, message = find_valid_email(soup, business_name)
        if email:
            return email, message
        
        # If no valid email found and we haven't reached max depth, look for contact page
        if max_depth > 0:
            # Look for contact page link
            contact_links = soup.find_all('a', href=True)
            for link in contact_links:
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                # Check if this is likely a contact page
                if any(term in href or term in text for term in ['contact', 'about', 'reach', 'get-in-touch']):
                    # Make sure the URL is absolute
                    if not href.startswith(('http://', 'https://')):
                        if href.startswith('/'):
                            href = url.rstrip('/') + href
                        else:
                            href = url.rstrip('/') + '/' + href
                    
                    # Recursively search contact page
                    email, message = scrape_business_website(href, business_name, max_depth - 1)
                    if email:
                        return email, message
        
        return None, "No valid email found after checking all pages"
        
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"
    except Exception as e:
        return None, f"Error scraping website: {str(e)}"

if __name__ == "__main__":
    # Test the scraper with various business websites
    test_urls = [
        "https://www.legalzoom.com",
        "https://www.avvo.com",
        "https://www.findlaw.com",
        "https://www.example.com",
    ]
    
    for url in test_urls:
        print(f"\nTesting URL: {url}")
        email, message = scrape_business_website(url, "Test Business")
        print(f"Email found: {email}")
        print(f"Message: {message}")
        print("-" * 50) 