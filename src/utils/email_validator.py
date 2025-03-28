import dns.resolver
import re
from typing import Tuple

def is_valid_email_format(email: str) -> bool:
    """Check if email follows valid format."""
    if not email or not isinstance(email, str):
        return False
        
    # Check for consecutive dots
    if '..' in email:
        return False
        
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def check_dns_records(domain: str) -> Tuple[bool, str]:
    """Check if domain has valid MX records."""
    try:
        # Check for MX records
        mx_records = dns.resolver.resolve(domain, 'MX')
        if mx_records:
            return True, "Valid MX records found"
        return False, "No MX records found"
    except dns.resolver.NoAnswer:
        return False, "No MX records found"
    except dns.resolver.NXDOMAIN:
        return False, "Domain does not exist"
    except Exception as e:
        return False, f"Error checking DNS: {str(e)}"

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email address using multiple methods."""
    # First check format
    if not email or not isinstance(email, str):
        return False, "No email provided"
        
    if not is_valid_email_format(email):
        return False, "Invalid email format"
    
    # Extract domain
    domain = email.split('@')[1]
    
    # Skip validation for common disposable email domains
    disposable_domains = {'tempmail.com', 'throwawaymail.com', 'tempmailaddress.com'}
    if domain in disposable_domains:
        return False, "Disposable email domain not allowed"
    
    # Check DNS records
    dns_valid, dns_message = check_dns_records(domain)
    if not dns_valid:
        return False, dns_message
    
    return True, "Email appears valid"

def validate_business_email(email: str, business_name: str) -> Tuple[bool, str]:
    """Validate business email with additional business-specific checks."""
    # Basic validation
    if not email or not isinstance(email, str):
        return False, "No email provided"
        
    is_valid, message = validate_email(email)
    if not is_valid:
        return False, message
    
    # Check if email domain matches business name
    domain = email.split('@')[1]
    business_domain = business_name.lower().replace(' ', '').replace('&', 'and')
    
    # Common business email patterns
    common_patterns = [
        f"{business_domain}.com",
        f"{business_domain}.org",
        f"{business_domain}.net",
        f"{business_domain}.biz"
    ]
    
    if domain not in common_patterns:
        return False, "Email domain does not match business name pattern"
    
    return True, "Business email appears valid"

if __name__ == "__main__":
    # Test the validation
    test_emails = [
        "info@goodmanacker.com",
        "contact@invalid-domain.com",
        "test@example.com",
        "invalid-email"
    ]
    
    for email in test_emails:
        is_valid, message = validate_email(email)
        print(f"Email: {email}")
        print(f"Valid: {is_valid}")
        print(f"Message: {message}")
        print("---") 