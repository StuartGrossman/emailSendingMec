#!/usr/bin/env python3
import requests
import json
import os
import random
import time
import logging
import re
import dns.resolver
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
from multiprocessing import Pool, Manager, Lock
from bs4 import BeautifulSoup
from src.config.config import (
    LOG_LEVEL, LOG_FILE, NUM_PROCESSES, RATE_LIMIT_DELAY, REQUEST_TIMEOUT,
    GROK_API_KEYS, FIREBASE_URL
)
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Import the business types and cities from the original scraper
from src.scrapers.business_scraper import MAJOR_CITIES, BUSINESS_TYPES

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

class BusinessScraper:
    def __init__(self, api_key: str, process_id: int):
        self.api_key = api_key
        self.process_id = process_id
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.logger = logging.getLogger(f"Process-{process_id}")
        # Initialize statistics
        self.stats = {
            'total_businesses': 0,
            'rejected_businesses': 0,
            'saved_businesses': 0,
            'api_requests': 0,
            'rejection_reasons': {},
            'start_time': datetime.now().isoformat()
        }

    def find_valid_email(self, soup: BeautifulSoup, business_name: str) -> Tuple[Optional[str], str]:
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
        
        # First try to find email in meta tags (fastest check)
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
                    if self.validate_email(email):
                        return email, "Valid email found in meta tags"
        
        # Look for email in mailto links (second fastest check)
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if href.startswith('mailto:'):
                email = href[7:]  # Remove 'mailto:' prefix
                if self.validate_email(email):
                    return email, "Valid email found in mailto link"
        
        # Look for contact forms (third fastest check)
        forms = soup.find_all('form')
        for form in forms:
            # Check form action for email
            action = form.get('action', '')
            if 'mailto:' in action:
                email = action.split('mailto:')[1].split('?')[0]
                if self.validate_email(email):
                    return email, "Valid email found in form action"
        
        # Look for email in text content (slowest check, but most thorough)
        text_content = soup.get_text()
        for pattern in email_patterns:
            matches = re.findall(pattern, text_content)
            for email in matches:
                # Clean up the email
                email = re.sub(r'\s*\[at\]\s*', '@', email)
                email = re.sub(r'\s*\(at\)\s*', '@', email)
                email = re.sub(r'\s*@\s*', '@', email)
                
                # Validate the email
                if self.validate_email(email):
                    return email, "Valid email found in text content"
        
        return None, "No valid email found on page"

    def scrape_business_website(self, url: str, business_name: str, max_depth: int = 2) -> Tuple[Optional[str], str]:
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
            email, message = self.find_valid_email(soup, business_name)
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
                        email, message = self.scrape_business_website(href, business_name, max_depth - 1)
                        if email:
                            return email, message
            
            return None, "No valid email found after checking all pages"
            
        except requests.exceptions.RequestException as e:
            return None, f"Network error: {str(e)}"
        except Exception as e:
            return None, f"Error scraping website: {str(e)}"

    def validate_email(self, email: str) -> bool:
        """Validate email format and check if domain has MX records."""
        if not email or email.lower() == 'null':
            return False
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False
        
        # Extract domain
        domain = email.split('@')[1]
        
        # Skip validation for common disposable email domains
        disposable_domains = {'tempmail.com', 'throwawaymail.com', 'tempmailaddress.com'}
        if domain in disposable_domains:
            return False
            
        try:
            # Check for MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            if not mx_records:
                return False
                
            # Additional check: Verify the MX record is not a catch-all or spam domain
            mx_string = str(mx_records[0]).lower()
            spam_indicators = {'spam', 'catch-all', 'bounce', 'invalid'}
            if any(indicator in mx_string for indicator in spam_indicators):
                return False
                
            return True
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            return False

    def is_small_business(self, business: Dict) -> bool:
        """Check if a business meets small business criteria."""
        # Skip if no description
        if not business.get("description"):
            return False

        description = business["description"].lower()
        
        # Skip if description indicates a large business
        large_business_indicators = [
            "corporation", "corp", "inc", "ltd", "limited",
            "franchise", "chain", "national", "international",
            "headquarters", "branch", "subsidiary", "division",
            "manufacturing", "production", "warehouse", "distribution",
            "wholesale", "retail chain", "department store",
            "restaurant chain", "franchise location", "corporate office"
        ]
        
        if any(indicator in description for indicator in large_business_indicators):
            return False

        # Check employee count if available
        employees = business.get("employees")
        if employees:
            try:
                # Handle various formats
                if isinstance(employees, str):
                    # Remove any non-numeric characters except hyphens
                    employees = re.sub(r'[^\d-]', '', employees)
                    
                    # Handle ranges (e.g., "1-10", "1 to 10")
                    if '-' in employees or ' to ' in employees:
                        max_employees = int(employees.split('-')[-1].split(' to ')[-1])
                    else:
                        max_employees = int(employees)
                    
                    if max_employees > 1000:  # Increased from 500 to 1000
                        return False
                else:
                    max_employees = int(employees)
                    if max_employees > 1000:  # Increased from 500 to 1000
                        return False
            except (ValueError, TypeError):
                return False

        return True

    def validate_website(self, url: str) -> bool:
        """Validate website URL and check if it exists."""
        if not url:
            return False
        
        # Basic URL validation
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return False
        except Exception:
            return False
        
        # Check DNS records
        try:
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check A records
            try:
                answers = dns.resolver.resolve(domain, 'A')
                if not answers:
                    return False
            except dns.resolver.NoAnswer:
                # If no A records, check CNAME
                try:
                    answers = dns.resolver.resolve(domain, 'CNAME')
                    if not answers:
                        return False
                except dns.resolver.NoAnswer:
                    return False
            
            return True
        except Exception:
            return False

    def validate_employee_count(self, employee_count: str) -> bool:
        """Validate employee count format."""
        if not employee_count:
            return False
        
        # Remove any whitespace and convert to lowercase
        employee_count = employee_count.strip().lower()
        
        # Handle various formats
        if employee_count.isdigit():
            return True
        elif employee_count.endswith('employees'):
            return employee_count[:-9].strip().isdigit()
        elif employee_count.endswith('employee'):
            return employee_count[:-8].strip().isdigit()
        elif employee_count.endswith('staff'):
            return employee_count[:-5].strip().isdigit()
        elif employee_count.endswith('people'):
            return employee_count[:-6].strip().isdigit()
        elif employee_count.endswith('+'):
            return employee_count[:-1].strip().isdigit()
        elif '-' in employee_count:
            parts = employee_count.split('-')
            return all(part.strip().isdigit() for part in parts)
        elif 'to' in employee_count:
            parts = employee_count.split('to')
            return all(part.strip().isdigit() for part in parts)
        
        return False

    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        if not phone:
            return False
        
        # Remove all non-numeric characters
        phone_digits = ''.join(filter(str.isdigit, phone))
        
        # Check if we have a valid number of digits (10 for US numbers)
        return len(phone_digits) == 10

    def clean_phone(self, phone: str) -> str:
        """Clean and format phone number."""
        if not phone:
            return None
        
        # Remove all non-numeric characters
        phone_digits = ''.join(filter(str.isdigit, phone))
        
        # Format as (XXX) XXX-XXXX if valid
        if len(phone_digits) == 10:
            return f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
        
        return None

    def clean_business_data(self, business: Dict) -> Dict:
        """Clean and validate business data."""
        # Create a copy to avoid modifying the original
        cleaned = business.copy()
        
        # Clean email
        email = cleaned.get('email', '')
        if email and isinstance(email, str):
            email = email.strip().lower()
            if not self.validate_email(email):
                cleaned['email'] = None
        else:
            cleaned['email'] = None
        
        # Clean website
        website = cleaned.get('website', '')
        if website and isinstance(website, str):
            website = website.strip()
            if not self.validate_website(website):
                cleaned['website'] = None
        else:
            cleaned['website'] = None
        
        # Clean phone
        phone = cleaned.get('phone', '')
        if phone and isinstance(phone, str):
            cleaned['phone'] = self.clean_phone(phone)
        else:
            cleaned['phone'] = None
        
        # Clean name
        name = cleaned.get('name', '')
        if name and isinstance(name, str):
            cleaned['name'] = name.strip()
        else:
            cleaned['name'] = ''
        
        # Clean description
        description = cleaned.get('description', '')
        if description and isinstance(description, str):
            cleaned['description'] = description.strip()
        else:
            cleaned['description'] = ''
        
        # Clean employees
        employees = cleaned.get('employees', '')
        if employees and isinstance(employees, str):
            cleaned['employees'] = employees.strip()
        else:
            cleaned['employees'] = ''
        
        return cleaned

    def update_stats(self, rejection_reason: str = None, saved: bool = False):
        """Update scraper statistics."""
        self.stats['total_businesses'] += 1
        if rejection_reason:
            self.stats['rejected_businesses'] += 1
            self.stats['rejection_reasons'][rejection_reason] = self.stats['rejection_reasons'].get(rejection_reason, 0) + 1
        if saved:
            self.stats['saved_businesses'] += 1
        self.stats['api_requests'] += 1

    def save_scraper_log(self):
        """Save scraper statistics to Firebase."""
        try:
            # Calculate duration
            start_time = datetime.fromisoformat(self.stats['start_time'])
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Prepare log data
            log_data = {
                'timestamp': end_time.isoformat(),
                'duration_seconds': duration,
                'total_businesses': self.stats['total_businesses'],
                'rejected_businesses': self.stats['rejected_businesses'],
                'saved_businesses': self.stats['saved_businesses'],
                'api_requests': self.stats['api_requests'],
                'rejection_reasons': self.stats['rejection_reasons'],
                'success_rate': f"{(self.stats['saved_businesses'] / self.stats['total_businesses'] * 100):.2f}%" if self.stats['total_businesses'] > 0 else "0%"
            }

            # Generate a unique log ID
            log_id = f"scrape_{end_time.strftime('%Y%m%d_%H%M%S')}_{self.process_id}"

            # Save to Firebase
            firebase_url = f"{FIREBASE_URL}/scraperLogs/{log_id}.json"
            response = requests.put(firebase_url, json=log_data)

            if response.status_code == 200:
                self.logger.info(f"Successfully saved scraper log with ID: {log_id}")
            else:
                self.logger.error(f"Failed to save scraper log: {response.status_code}")
                self.logger.error(f"Response text: {response.text}")

        except Exception as e:
            self.logger.error(f"Error saving scraper log: {str(e)}")

    def save_to_firebase(self, business: Dict, business_type: str, city: str, state: str) -> bool:
        """Save business data to Firebase"""
        try:
            # Clean and validate business data
            cleaned_business = {
                'name': business.get('name', '').strip(),
                'description': business.get('description', '').strip(),
                'website': business.get('website', '').strip(),
                'email': business.get('email', '').strip(),
                'phone': business.get('phone', '').strip(),
                'employees': business.get('employees', '').strip(),
                'city': city,
                'state': state,
                'type': business_type,
                'timestamp': datetime.now().isoformat()
            }

            # Check for valid email
            if not cleaned_business['email']:
                self.logger.warning(f"No valid email found for {cleaned_business['name']}")
                return False

            # Create a unique business ID
            business_id = f"{business_type}_{city}_{state}_{cleaned_business['name']}".lower()
            business_id = re.sub(r'[^a-z0-9]', '_', business_id)

            # Prepare business data with all required fields
            business_data = {
                'benefits': f"Custom software solutions for {business_type}",
                'development_time': "2-4 weeks",
                'estimated_cost': "Starting at $5,000",
                'features': [
                    "Custom business management",
                    "Automated workflows",
                    "Data analytics",
                    "Customer relationship management"
                ],
                'type': business_type,
                'timestamp': datetime.now().isoformat(),
                'website': cleaned_business['website'],
                'email': cleaned_business['email'],
                'phone': cleaned_business['phone'],
                'name': cleaned_business['name'],
                'description': cleaned_business['description'],
                'employees': cleaned_business['employees'],
                'city': cleaned_business['city'],
                'state': cleaned_business['state']
            }

            # Save to Firebase
            url = f"{FIREBASE_URL}/businesses/{business_id}.json"
            response = requests.put(url, json=business_data, timeout=REQUEST_TIMEOUT)

            if response.status_code == 200:
                # Update statistics
                self.stats['total_businesses'] += 1
                self.stats['saved_businesses'] += 1
                
                # Save API action tracking
                api_action = {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'save_business',
                    'business_type': business_type,
                    'city': city,
                    'state': state,
                    'business_name': cleaned_business['name'],
                    'success': True,
                    'stats': {
                        'total_businesses': self.stats['total_businesses'],
                        'saved_businesses': self.stats['saved_businesses'],
                        'rejected_businesses': self.stats['rejected_businesses'],
                        'api_requests': self.stats['api_requests']
                    }
                }
                
                # Save API action to Firebase
                action_url = f"{FIREBASE_URL}/apiActions/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{business_id}.json"
                requests.put(action_url, json=api_action, timeout=REQUEST_TIMEOUT)
                
                self.logger.info(f"Successfully saved business {cleaned_business['name']} to siteList")
                return True
            else:
                self.logger.error(f"Failed to save business to Firebase: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Error saving business to Firebase: {str(e)}")
            return False

    def save_rejected_business(self, business: Dict, rejection_reason: str, city: str, state: str, business_type: str) -> bool:
        """Save rejected business data to Firebase with improved error handling."""
        try:
            # Create a unique ID for the rejected business
            business_id = f"{business_type}_{city}_{business['name']}".lower()
            business_id = re.sub(r'[^a-z0-9]', '_', business_id)
            
            # Prepare rejected business data
            rejected_data = {
                'business_name': business['name'],
                'description': business.get('description', ''),
                'website': business.get('website', ''),
                'email': business.get('email', ''),
                'phone': business.get('phone', ''),
                'employees': business.get('employees', ''),
                'rejection_reason': rejection_reason,
                'city': city,
                'state': state,
                'business_type': business_type,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save to rejectedSiteList in Firebase
            firebase_url = f"{FIREBASE_URL}/rejectedSiteList/{business_id}.json"
            response = requests.put(firebase_url, json=rejected_data)
            
            if response.status_code == 200:
                self.logger.info(f"Successfully saved rejected business {business['name']} to rejectedSiteList")
                return True
            else:
                self.logger.error(f"Failed to save rejected business {business_id}: {response.status_code}")
                self.logger.error(f"Response text: {response.text}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error saving rejected business to Firebase: {str(e)}")
            return False

    def get_existing_businesses(self, city: str, state: str, business_type: str) -> Tuple[List[str], List[str]]:
        """Get lists of existing and rejected business names for a specific city and business type"""
        try:
            # Query both siteList and rejectedSiteList from Firebase using REST API
            site_list_url = f"{FIREBASE_URL}/siteList.json"
            rejected_url = f"{FIREBASE_URL}/rejectedSiteList.json"
            
            site_list_response = requests.get(site_list_url)
            rejected_response = requests.get(rejected_url)
            
            if site_list_response.status_code != 200 or rejected_response.status_code != 200:
                self.logger.error(f"Failed to get existing businesses: {site_list_response.status_code}, {rejected_response.status_code}")
                return [], []
            
            site_list_data = site_list_response.json() or {}
            rejected_data = rejected_response.json() or {}
            
            existing_names = []
            rejected_names = []
            
            # Filter businesses by city, state, and business type
            for business_id, business_data in site_list_data.items():
                if (business_data.get('metadata', {}).get('city') == city and 
                    business_data.get('metadata', {}).get('state') == state and 
                    business_data.get('metadata', {}).get('business_type') == business_type):
                    existing_names.append(business_data['name'].lower().strip())
            
            for business_id, business_data in rejected_data.items():
                if (business_data.get('city') == city and 
                    business_data.get('state') == state and 
                    business_data.get('business_type') == business_type):
                    rejected_names.append(business_data['business_name'].lower().strip())
            
            self.logger.info(f"Found {len(existing_names)} existing and {len(rejected_names)} rejected businesses for {business_type} in {city}, {state}")
            return existing_names, rejected_names
            
        except Exception as e:
            self.logger.error(f"Error getting existing businesses from Firebase: {str(e)}")
            return [], []

    def get_businesses_from_grok(self, city: str, state: str, business_type: str, 
                               description: str, software_probability: int, 
                               existing_names: List[str], lock: Lock) -> List[Dict]:
        """Get business information from Grok API for a specific business type in a city"""
        self.logger.info(f"Getting business information for {business_type} in {city}, {state}")
        
        # Get lists of existing and rejected businesses
        existing_names, rejected_names = self.get_existing_businesses(city, state, business_type)
        
        # Combine existing and rejected names
        all_excluded_names = list(set(existing_names + rejected_names))
        self.logger.info(f"Total excluded business names: {len(all_excluded_names)}")
        
        businesses = []
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1} of {max_retries} to get businesses from Grok API")
                
                prompt = f"""Find 5 real small businesses in {city} that are {business_type}. 
                For each business, provide:
                1. Name (must be a real, existing business)
                2. Description (2-3 sentences about their services and target market)
                3. Website URL (must be a real, existing website that is currently active)
                4. Email address (MUST be extracted from the website's HTML, specifically from:
                   - Contact page
                   - About page
                   - Footer
                   - Contact forms
                   - Business information sections
                   Do NOT make up or guess email addresses)
                5. Phone number (must be a valid US phone number)
                6. Number of employees (if available, must be less than 1000)
                
                Important requirements:
                - Only include real, existing businesses
                - Businesses must be independently owned (not chains or franchises)
                - Websites must be currently active and accessible
                - Email addresses MUST be found in the website's HTML
                - Phone numbers must be valid US numbers
                - Employee count must be less than 1000
                
                Format each business as a JSON object with these fields:
                {{
                    "name": "string",
                    "description": "string",
                    "website": "string or null",
                    "email": "string or null",
                    "phone": "string or null",
                    "employees": "string or null"
                }}
                
                Return a JSON array of these objects."""

                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=self.headers,
                    json={
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a business research assistant. Provide accurate business information in JSON format. Only include real, existing businesses that you can verify."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "model": "grok-2",
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    timeout=REQUEST_TIMEOUT
                )

                if response.status_code != 200:
                    self.logger.error(f"Grok API returned non-200 status code: {response.status_code}")
                    self.logger.error(f"Response text: {response.text}")
                    time.sleep(retry_delay)
                    continue

                response_json = response.json()
                content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if not content or content.strip() == "":
                    self.logger.error("Grok API returned empty response")
                    time.sleep(retry_delay)
                    continue

                try:
                    # Clean the content string to ensure it's valid JSON
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                    
                    businesses_data = json.loads(content)
                    if not isinstance(businesses_data, list):
                        self.logger.error("Grok API returned invalid response format")
                        self.logger.error(f"Response content: {content}")
                        time.sleep(retry_delay)
                        continue

                    self.logger.info(f"Successfully parsed {len(businesses_data)} businesses from Grok API response")

                    for business in businesses_data:
                        if not isinstance(business, dict):
                            self.logger.error(f"Invalid business entry: {business}")
                            continue

                        # Skip if business name is in excluded list
                        business_name = business.get('name', '').lower().strip()
                        if business_name in all_excluded_names:
                            self.logger.info(f"Skipping excluded business: {business_name}")
                            continue

                        # Log business details for debugging
                        self.logger.info(f"Processing business: {business.get('name', 'unknown')}")
                        self.logger.info(f"Website: {business.get('website', 'None')}")
                        self.logger.info(f"Email: {business.get('email', 'None')}")
                        self.logger.info(f"Phone: {business.get('phone', 'None')}")
                        self.logger.info(f"Employees: {business.get('employees', 'None')}")

                        # Validate required fields
                        required_fields = ["name", "description"]
                        if not all(field in business for field in required_fields):
                            self.logger.error(f"Business missing required fields: {business}")
                            continue

                        # Validate website if present
                        if business.get("website"):
                            if not self.validate_website(business["website"]):
                                self.logger.warning(f"Invalid website for {business['name']}: {business['website']}")
                                business["website"] = None
                            else:
                                self.logger.info(f"Valid website found for {business['name']}")

                        # Validate email if present
                        if business.get("email"):
                            if not self.validate_email(business["email"]):
                                self.logger.warning(f"Invalid email for {business['name']}: {business['email']}")
                                business["email"] = None
                            else:
                                self.logger.info(f"Valid email found for {business['name']}")

                        # If no valid email but valid website, try to scrape email
                        if not business.get("email") and business.get("website"):
                            self.logger.info(f"Attempting to scrape email from website: {business['website']}")
                            email, message = self.scrape_business_website(business["website"], business["name"])
                            if email:
                                self.logger.info(f"Found valid email through scraping: {email}")
                                business["email"] = email
                            else:
                                self.logger.warning(f"Could not find valid email through scraping: {message}")

                        # Validate phone if present
                        if business.get("phone"):
                            if not self.validate_phone(business["phone"]):
                                self.logger.warning(f"Invalid phone for {business['name']}: {business['phone']}")
                                business["phone"] = None
                            else:
                                self.logger.info(f"Valid phone found for {business['name']}")

                        businesses.append(business)
                        self.logger.info(f"Successfully processed business: {business['name']}")

                    return businesses

                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parsing Grok API response: {e}")
                    self.logger.error(f"Content that failed to parse: {content}")
                    time.sleep(retry_delay)
                    continue

            except Exception as e:
                self.logger.error(f"Error making request to Grok API: {str(e)}")
                time.sleep(retry_delay)
                continue

        self.logger.warning(f"Failed to get valid businesses after {max_retries} attempts")
        return businesses

def process_city_group(args):
    """Process a group of cities with a specific API key"""
    cities, api_key, process_id, existing_names, lock = args
    scraper = BusinessScraper(api_key, process_id)
    
    try:
        for city, state in cities:
            for business_type, software_probability, description in BUSINESS_TYPES:
                businesses = scraper.get_businesses_from_grok(
                    city, state, business_type, description, 
                    software_probability, existing_names, lock
                )
                
                if businesses:
                    for business in businesses:
                        success = scraper.save_to_firebase(business, business_type, city, state)
                        if success:
                            with lock:
                                if business['name'].lower().strip() not in existing_names:
                                    existing_names.append(business['name'].lower().strip())
                
                # Add delay between requests to avoid rate limiting
                time.sleep(RATE_LIMIT_DELAY)
    finally:
        # Save scraper log when done
        scraper.save_scraper_log()

def main():
    print("Parallel Business Information Scraper using Grok")
    print("=" * 50)
    
    # Create a manager for shared state
    manager = Manager()
    existing_names = manager.list()
    lock = manager.Lock()
    
    # Split cities into groups for parallel processing
    cities_per_process = len(MAJOR_CITIES) // NUM_PROCESSES
    city_groups = [MAJOR_CITIES[i:i + cities_per_process] for i in range(0, len(MAJOR_CITIES), cities_per_process)]
    
    # Prepare arguments for each process
    process_args = [
        (group, api_key, i, existing_names, lock)
        for i, (group, api_key) in enumerate(zip(city_groups, GROK_API_KEYS))
    ]
    
    # Create and run the process pool
    with Pool(processes=NUM_PROCESSES) as pool:
        pool.map(process_city_group, process_args)
    
    print("\nScraping completed!")

if __name__ == "__main__":
    main() 