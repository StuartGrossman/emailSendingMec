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
from typing import List, Dict, Set, Tuple
from multiprocessing import Pool, Manager, Lock
from config import (
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
from business_scraper import MAJOR_CITIES, BUSINESS_TYPES

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
        
        try:
            # Check for MX records
            dns.resolver.resolve(domain, 'MX')
            return True
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            return False

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
        """Save business data to Firebase with improved error handling."""
        try:
            # Clean and validate business data
            cleaned_business = self.clean_business_data(business)
            
            # Check if business has valid email (primary requirement)
            if not cleaned_business.get('email'):
                self.save_rejected_business(business, 'no_valid_email', city, state, business_type)
                self.update_stats(rejection_reason='no_valid_email')
                return False
            
            # Create a unique ID for the business
            business_id = f"{business_type}_{city}_{cleaned_business['name']}".lower()
            business_id = re.sub(r'[^a-z0-9]', '_', business_id)
            
            # Add metadata
            cleaned_business['metadata'] = {
                'business_type': business_type,
                'city': city,
                'state': state,
                'last_updated': datetime.now().isoformat(),
                'source': 'grok_api'
            }
            
            # Save to siteList in Firebase
            firebase_url = f"{FIREBASE_URL}/siteList/{business_id}.json"
            response = requests.put(firebase_url, json=cleaned_business)
            
            if response.status_code == 200:
                self.logger.info(f"Successfully saved business {cleaned_business['name']} to siteList")
                self.update_stats(saved=True)
                return True
            else:
                self.logger.error(f"Failed to save business {business_id}: {response.status_code}")
                self.logger.error(f"Response text: {response.text}")
                return False
            
        except Exception as e:
            self.logger.error(f"Error saving business {business.get('name', 'Unknown')}: {str(e)}")
            self.logger.error(f"Full business data: {json.dumps(business, indent=2)}")
            self.update_stats(rejection_reason='firebase_save_error')
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
        retry_delay = 5  # seconds

        for attempt in range(max_retries):
            try:
                self.logger.info(f"Attempt {attempt + 1} of {max_retries} to get businesses from Grok API")
                
                prompt = f"""Find 5 real small businesses in {city} that are {business_type}. 
                For each business, provide:
                1. Name (must be a real, existing business)
                2. Description (2-3 sentences about their services and target market)
                3. Website URL (must be a real, existing website that is currently active)
                4. Email address (if available, must be a valid business email)
                5. Phone number (if available, must be a valid US phone number)
                6. Number of employees (if available, must be less than 1000)
                
                Important requirements:
                - Only include real, existing businesses
                - Businesses must be independently owned (not chains or franchises)
                - Websites must be currently active and accessible
                - Email addresses must be valid business emails
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