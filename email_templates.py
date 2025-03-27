#!/usr/bin/env python3
import json
import requests
from typing import Dict, List, Tuple
from datetime import datetime

# Email templates with their target criteria
EMAIL_TEMPLATES = {
    "general": {
        "name": "Modern Software – Faster, Cheaper, Yours to Own",
        "template": """Hi,

Custom software used to be complex and expensive—not anymore. Advances in technology have made it faster and more affordable than ever to build powerful tools tailored specifically to your business.

I specialize in developing high-quality, efficient software that streamlines operations, saves time, and gives you full ownership of the code. Whether it's automating inventory, optimizing scheduling, or improving customer management, I can help.

If you've ever thought, "We'd love custom software, but it's too expensive or complicated," those days are over. Let's chat about how technology can bring your business to its highest technical state at a fraction of the cost you might expect.

Would you be open to a quick call?

Best,
Stuart Grossman
4159994541""",
        "criteria": {
            "min_software_probability": 7,
            "business_types": ["Retail Boutiques", "Local Restaurants", "Real Estate Agencies", 
                             "Medical Practices", "Legal Firms", "Educational Centers", 
                             "Interior Design Firms", "Marketing Agencies"]
        }
    },
    "automation": {
        "name": "Automate Your Business – Faster, Smarter, Affordable",
        "template": """Hi,

If your team is spending hours on manual tasks, you're leaving money on the table. Custom software can automate client management, scheduling, reports, and other time-consuming processes—without breaking the bank.

I build efficient, modern software solutions tailored to businesses like yours, using best practices to ensure speed, reliability, and scalability. Plus, you own the code, giving you full control.

If you've ever had a software idea but thought it was too complex or too expensive, now is the time to revisit it. Let's discuss how we can make your business run smoother than ever.

Would you be open to a quick call?

Best,
Stuart Grossman
4159994541""",
        "criteria": {
            "min_software_probability": 6,
            "business_types": ["Construction Companies", "Manufacturing Workshops", "Fitness Studios", 
                             "Beauty Salons", "Auto Repair Shops", "Event Planning Services", 
                             "Cleaning Services", "Landscaping Services", "Pet Services", 
                             "Artisan Workshops", "Food Production", "Photography Studios"]
        }
    },
    "compliance": {
        "name": "Secure, Custom Software – Fast & Cost-Effective - Tailored for you",
        "template": """Hi,

Compliance, security, and efficiency shouldn't be a bottleneck in your business. With modern tools, custom software is now faster and more affordable than ever, making it the perfect time to upgrade outdated systems.

I specialize in developing secure, high-performance software that ensures compliance while optimizing workflows—whether it's automated reporting, fraud detection, or secure client management. Best of all, you own the code, giving you full control over your solution.

If you've ever wanted a custom system but thought it was too complex or costly, let's talk. The game has changed, and it's in your best interest to leverage today's technology for maximum efficiency.

Would you be open to a quick call?

Best,
Stuart Grossman
4159994541""",
        "criteria": {
            "min_software_probability": 8,
            "business_types": ["Legal Firms", "Medical Practices", "Real Estate Agencies", 
                             "Marketing Agencies", "Educational Centers"]
        }
    },
    "niche": {
        "name": "Cutting-Edge Tech – Custom & Cost-Effective - Tailored for you",
        "template": """Hi,

Innovation moves fast—does your software keep up? Custom-built solutions are now more affordable than ever, allowing businesses like yours to leverage AI, automation, and smart technology without breaking the bank.

I build high-performance software tailored to emerging industries, helping businesses integrate modern solutions quickly and efficiently. And unlike SaaS platforms, you own the code—giving you full control and scalability.

If you've ever had an idea but thought it was too complex or expensive, let's chat. The barriers to powerful, custom technology have never been lower.

Would you be open to a quick call?

Best,
Stuart Grossman
4159994541""",
        "criteria": {
            "min_software_probability": 7,
            "business_types": ["Event Planning Services", "Interior Design Firms", "Photography Studios", 
                             "Artisan Workshops", "Food Production"]
        }
    }
}

def get_businesses_from_firebase() -> Dict:
    """Fetch all businesses from Firebase"""
    print("Fetching businesses from Firebase...")
    
    firebase_url = "https://emailsender-44bcc-default-rtdb.firebaseio.com/siteList.json"
    
    try:
        response = requests.get(firebase_url)
        if response.status_code == 200:
            businesses = response.json() or {}
            print(f"Found {len(businesses)} businesses")
            return businesses
        else:
            print(f"Failed to fetch businesses: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error fetching businesses: {str(e)}")
        return {}

def match_business_to_template(business: Dict) -> Tuple[str, str]:
    """Match a business to the most appropriate email template"""
    best_match = None
    best_score = 0
    
    for template_name, template_data in EMAIL_TEMPLATES.items():
        criteria = template_data["criteria"]
        
        # Check if business meets minimum software probability
        if business.get('software_probability', 0) < criteria['min_software_probability']:
            continue
            
        # Check if business type matches
        if business.get('business_type') in criteria['business_types']:
            # Calculate match score based on software probability
            score = business.get('software_probability', 0)
            if score > best_score:
                best_score = score
                best_match = template_name
    
    if best_match:
        return best_match, EMAIL_TEMPLATES[best_match]["template"]
    else:
        # Default to general template if no specific match
        return "general", EMAIL_TEMPLATES["general"]["template"]

def generate_email_content(business: Dict, template: str) -> str:
    """Generate personalized email content for a business"""
    # Add business-specific personalization
    personalized_template = template.replace("Hi,", f"Hi {business['name']},")
    return personalized_template

def save_email_to_firebase(business: Dict, template_name: str, email_content: str):
    """Save generated email to Firebase"""
    try:
        # Clean business name for use in key
        clean_name = ''.join(c for c in business['name'] if c.isalnum() or c.isspace())
        clean_name = clean_name.replace(' ', '_')
        
        # Prepare email data
        email_data = {
            'business_name': business['name'],
            'email': business['email'],
            'template_used': template_name,
            'content': email_content,
            'generated_at': datetime.now().isoformat(),
            'status': 'pending'  # pending, sent, failed
        }
        
        # Save to Firebase
        firebase_url = f"https://emailsender-44bcc-default-rtdb.firebaseio.com/emails/{clean_name}.json"
        response = requests.put(firebase_url, json=email_data)
        
        if response.status_code == 200:
            print(f"Successfully saved email for {business['name']}")
        else:
            print(f"Failed to save email for {business['name']}: {response.status_code}")
            
    except Exception as e:
        print(f"Error saving email for {business['name']}: {str(e)}")

def main():
    print("Email Template Matcher")
    print("=" * 50)
    
    # Get all businesses from Firebase
    businesses = get_businesses_from_firebase()
    
    if not businesses:
        print("No businesses found in Firebase")
        return
    
    # Process each business
    for business_name, business_data in businesses.items():
        print(f"\nProcessing business: {business_data['name']}")
        
        # Match business to appropriate template
        template_name, template = match_business_to_template(business_data)
        print(f"Matched with template: {template_name}")
        
        # Generate personalized email content
        email_content = generate_email_content(business_data, template)
        
        # Save email to Firebase
        save_email_to_firebase(business_data, template_name, email_content)
        
        print("-" * 50)
    
    print("\nEmail template matching completed!")

if __name__ == "__main__":
    main() 