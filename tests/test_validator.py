#!/usr/bin/env python3
import json
import os
import requests
import dns.resolver
import re
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.parse import urlparse
import sys
import pytest

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.email_validator import validate_email, validate_business_email, is_valid_email_format

class DataValidator:
    def __init__(self):
        self.validation_results = {
            'total_businesses': 0,
            'valid_websites': 0,
            'valid_emails': 0,
            'valid_phones': 0,
            'valid_employee_counts': 0,
            'errors': [],
            'warnings': []
        }

    def validate_website(self, url: str) -> Tuple[bool, str]:
        """Validate website URL and check if it exists."""
        if not url:
            return False, "No URL provided"
        
        try:
            # Basic URL validation
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return False, "Invalid URL format"
            
            # Check DNS records
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check A records
            try:
                answers = dns.resolver.resolve(domain, 'A')
                if not answers:
                    return False, "No A records found"
            except dns.resolver.NoAnswer:
                # If no A records, check CNAME
                try:
                    answers = dns.resolver.resolve(domain, 'CNAME')
                    if not answers:
                        return False, "No DNS records found"
                except dns.resolver.NoAnswer:
                    return False, "No DNS records found"
            
            # Try to make a request
            try:
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    return False, f"Website returned status code {response.status_code}"
            except requests.RequestException as e:
                return False, f"Website request failed: {str(e)}"
            
            return True, "Website is valid"
            
        except Exception as e:
            return False, f"Website validation error: {str(e)}"

    def validate_email(self, email: str) -> Tuple[bool, str]:
        """Validate email format and check if domain has MX records."""
        if not email:
            return False, "No email provided"
        
        # Basic email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        # Extract domain
        domain = email.split('@')[1]
        
        try:
            # Check for MX records
            dns.resolver.resolve(domain, 'MX')
            return True, "Email is valid"
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            return False, "No MX records found for domain"

    def validate_phone(self, phone: str) -> Tuple[bool, str]:
        """Validate phone number format."""
        if not phone:
            return False, "No phone number provided"
        
        # Remove all non-numeric characters
        phone_digits = ''.join(filter(str.isdigit, phone))
        
        # Check if we have a valid number of digits (10 for US numbers)
        if len(phone_digits) != 10:
            return False, "Invalid phone number length"
        
        return True, "Phone number is valid"

    def validate_employee_count(self, count: str) -> Tuple[bool, str]:
        """Validate employee count format."""
        if not count:
            return False, "No employee count provided"
        
        # Remove any whitespace and convert to lowercase
        count = count.strip().lower()
        
        # Handle various formats
        if count.isdigit():
            return True, "Employee count is valid"
        elif count.endswith('employees'):
            return count[:-9].strip().isdigit(), "Employee count is valid"
        elif count.endswith('employee'):
            return count[:-8].strip().isdigit(), "Employee count is valid"
        elif count.endswith('staff'):
            return count[:-5].strip().isdigit(), "Employee count is valid"
        elif count.endswith('people'):
            return count[:-6].strip().isdigit(), "Employee count is valid"
        elif count.endswith('+'):
            return count[:-1].strip().isdigit(), "Employee count is valid"
        elif '-' in count:
            parts = count.split('-')
            return all(part.strip().isdigit() for part in parts), "Employee count is valid"
        elif 'to' in count:
            parts = count.split('to')
            return all(part.strip().isdigit() for part in parts), "Employee count is valid"
        
        return False, "Invalid employee count format"

    def validate_business(self, business: Dict) -> Dict:
        """Validate all fields of a business entry."""
        validation = {
            'name': business.get('name', ''),
            'website_valid': False,
            'email_valid': False,
            'phone_valid': False,
            'employee_count_valid': False,
            'errors': [],
            'warnings': []
        }
        
        # Validate website
        website_valid, website_message = self.validate_website(business.get('website', ''))
        validation['website_valid'] = website_valid
        if not website_valid:
            validation['errors'].append(f"Website: {website_message}")
        
        # Validate email
        email_valid, email_message = self.validate_email(business.get('email', ''))
        validation['email_valid'] = email_valid
        if not email_valid:
            validation['errors'].append(f"Email: {email_message}")
        
        # Validate phone
        phone_valid, phone_message = self.validate_phone(business.get('phone', ''))
        validation['phone_valid'] = phone_valid
        if not phone_valid:
            validation['errors'].append(f"Phone: {phone_message}")
        
        # Validate employee count
        employee_valid, employee_message = self.validate_employee_count(business.get('employees', ''))
        validation['employee_count_valid'] = employee_valid
        if not employee_valid:
            validation['warnings'].append(f"Employee count: {employee_message}")
        
        return validation

    def validate_data_file(self, file_path: str) -> Dict:
        """Validate all businesses in a data file."""
        try:
            with open(file_path, 'r') as f:
                businesses = json.load(f)
            
            self.validation_results['total_businesses'] = len(businesses)
            
            for business in businesses:
                validation = self.validate_business(business)
                
                if validation['website_valid']:
                    self.validation_results['valid_websites'] += 1
                if validation['email_valid']:
                    self.validation_results['valid_emails'] += 1
                if validation['phone_valid']:
                    self.validation_results['valid_phones'] += 1
                if validation['employee_count_valid']:
                    self.validation_results['valid_employee_counts'] += 1
                
                if validation['errors']:
                    self.validation_results['errors'].append({
                        'business': validation['name'],
                        'errors': validation['errors']
                    })
                
                if validation['warnings']:
                    self.validation_results['warnings'].append({
                        'business': validation['name'],
                        'warnings': validation['warnings']
                    })
            
            return self.validation_results
            
        except Exception as e:
            print(f"Error validating data file: {str(e)}")
            return None

def run_validation_tests():
    # Get the most recent test data file
    test_data_dir = 'testData'
    if not os.path.exists(test_data_dir):
        print("No test data directory found. Please run test_scraper.py first.")
        return
    
    files = [f for f in os.listdir(test_data_dir) if f.endswith('.json')]
    if not files:
        print("No test data files found. Please run test_scraper.py first.")
        return
    
    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(test_data_dir, x)))
    file_path = os.path.join(test_data_dir, latest_file)
    
    print(f"Validating data from: {file_path}")
    
    validator = DataValidator()
    results = validator.validate_data_file(file_path)
    
    if results:
        print("\nValidation Results:")
        print("=" * 50)
        print(f"Total businesses: {results['total_businesses']}")
        print(f"Valid websites: {results['valid_websites']} ({results['valid_websites']/results['total_businesses']*100:.1f}%)")
        print(f"Valid emails: {results['valid_emails']} ({results['valid_emails']/results['total_businesses']*100:.1f}%)")
        print(f"Valid phones: {results['valid_phones']} ({results['valid_phones']/results['total_businesses']*100:.1f}%)")
        print(f"Valid employee counts: {results['valid_employee_counts']} ({results['valid_employee_counts']/results['total_businesses']*100:.1f}%)")
        
        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"\n{error['business']}:")
                for e in error['errors']:
                    print(f"  - {e}")
        
        if results['warnings']:
            print("\nWarnings:")
            for warning in results['warnings']:
                print(f"\n{warning['business']}:")
                for w in warning['warnings']:
                    print(f"  - {w}")
        
        # Save validation results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f'testData/validation_results_{timestamp}.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nValidation results saved to: {results_file}")

def test_email_validation():
    """Test basic email validation."""
    assert validate_email("test@example.com")[0] == True
    assert validate_email("invalid-email")[0] == False
    assert validate_email("")[0] == False
    assert validate_email(None)[0] == False

def test_business_email_validation():
    """Test business-specific email validation."""
    # Test with matching domain
    assert validate_business_email("info@acmewidgets.com", "Acme Widgets")[0] == True
    
    # Test with non-matching domain
    assert validate_business_email("info@different.com", "Acme Widgets")[0] == False
    
    # Test with invalid email
    assert validate_business_email("invalid-email", "Test Business")[0] == False
    
    # Test with empty values
    assert validate_business_email("", "Test Business")[0] == False
    assert validate_business_email(None, "Test Business")[0] == False

def test_email_format_validation():
    """Test email format validation."""
    valid_emails = [
        "test@example.com",
        "test.name@example.com",
        "test+label@example.com",
        "test@sub.example.com"
    ]
    
    invalid_emails = [
        "test@",
        "@example.com",
        "test@.com",
        "test@example.",
        "test@exam ple.com",
        "test@example..com"
    ]
    
    for email in valid_emails:
        assert is_valid_email_format(email) == True, f"Failed for valid email: {email}"
        
    for email in invalid_emails:
        assert is_valid_email_format(email) == False, f"Failed for invalid email: {email}"

if __name__ == "__main__":
    run_validation_tests() 