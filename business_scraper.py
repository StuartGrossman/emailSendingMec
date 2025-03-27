#!/usr/bin/env python3
import requests
import json
import os
import random
from datetime import datetime
from typing import List, Dict, Set, Tuple

# Major US cities with their states
MAJOR_CITIES = [
    # Northeast
    ("New York", "NY"),
    ("Philadelphia", "PA"),
    ("Boston", "MA"),
    ("Pittsburgh", "PA"),
    ("Buffalo", "NY"),
    ("Rochester", "NY"),
    ("Albany", "NY"),
    ("Hartford", "CT"),
    ("Providence", "RI"),
    ("Worcester", "MA"),
    
    # Southeast
    ("Miami", "FL"),
    ("Atlanta", "GA"),
    ("Charlotte", "NC"),
    ("Orlando", "FL"),
    ("Tampa", "FL"),
    ("Jacksonville", "FL"),
    ("Raleigh", "NC"),
    ("Richmond", "VA"),
    ("Louisville", "KY"),
    ("Nashville", "TN"),
    ("Birmingham", "AL"),
    ("Memphis", "TN"),
    ("Columbia", "SC"),
    ("Charleston", "SC"),
    ("Savannah", "GA"),
    
    # Midwest
    ("Chicago", "IL"),
    ("Detroit", "MI"),
    ("Indianapolis", "IN"),
    ("Columbus", "OH"),
    ("Cincinnati", "OH"),
    ("Cleveland", "OH"),
    ("Milwaukee", "WI"),
    ("Minneapolis", "MN"),
    ("St. Louis", "MO"),
    ("Kansas City", "MO"),
    ("Omaha", "NE"),
    ("Des Moines", "IA"),
    ("Madison", "WI"),
    ("Grand Rapids", "MI"),
    ("Toledo", "OH"),
    
    # Southwest
    ("Dallas", "TX"),
    ("Houston", "TX"),
    ("Austin", "TX"),
    ("San Antonio", "TX"),
    ("Phoenix", "AZ"),
    ("Denver", "CO"),
    ("Las Vegas", "NV"),
    ("Albuquerque", "NM"),
    ("Tucson", "AZ"),
    ("Colorado Springs", "CO"),
    ("Oklahoma City", "OK"),
    ("Tulsa", "OK"),
    ("El Paso", "TX"),
    ("Fort Worth", "TX"),
    ("San Diego", "CA"),
    
    # West Coast
    ("Los Angeles", "CA"),
    ("San Francisco", "CA"),
    ("Seattle", "WA"),
    ("Portland", "OR"),
    ("Sacramento", "CA"),
    ("San Jose", "CA"),
    ("Oakland", "CA"),
    ("Fresno", "CA"),
    ("Spokane", "WA"),
    ("Eugene", "OR"),
    ("Boise", "ID"),
    ("Salt Lake City", "UT"),
    ("Reno", "NV"),
    ("Bakersfield", "CA"),
    ("Modesto", "CA"),
    
    # Small Towns (Population 250k-500k)
    ("Boulder", "CO"),
    ("Santa Fe", "NM"),
    ("Bend", "OR"),
    ("Asheville", "NC"),
    ("Chattanooga", "TN"),
    ("Greenville", "SC"),
    ("Knoxville", "TN"),
    ("Lexington", "KY"),
    ("Ann Arbor", "MI"),
    ("Fort Collins", "CO"),
    ("Bozeman", "MT"),
    ("Flagstaff", "AZ"),
    ("Santa Barbara", "CA"),
    ("Eugene", "OR"),
    ("Bellingham", "WA"),
    ("Durham", "NC"),
    ("Winston-Salem", "NC"),
    ("Green Bay", "WI"),
    ("Duluth", "MN"),
    ("Sioux Falls", "SD"),
    ("Lincoln", "NE"),
    ("Fargo", "ND"),
    ("Billings", "MT"),
    ("Missoula", "MT"),
    ("Anchorage", "AK"),
    ("Honolulu", "HI"),
    ("Burlington", "VT"),
    ("Portsmouth", "NH"),
    ("Bangor", "ME"),
    ("Augusta", "ME")
]

# Business types with their software need probability scores (1-10)
# Higher score means more likely to need custom software and easier to implement
BUSINESS_TYPES = [
    ("Retail Boutiques", 8, "Small retail stores specializing in specific products"),
    ("Local Restaurants", 7, "Independent restaurants and cafes"),
    ("Real Estate Agencies", 9, "Small real estate offices"),
    ("Medical Practices", 8, "Small medical clinics and practices"),
    ("Legal Firms", 9, "Small law offices"),
    ("Construction Companies", 7, "Local construction and contracting businesses"),
    ("Manufacturing Workshops", 6, "Small manufacturing and production facilities"),
    ("Educational Centers", 8, "Private schools and tutoring centers"),
    ("Fitness Studios", 7, "Local gyms and fitness centers"),
    ("Beauty Salons", 6, "Local salons and spas"),
    ("Auto Repair Shops", 6, "Local auto repair and maintenance shops"),
    ("Event Planning Services", 8, "Small event planning businesses"),
    ("Cleaning Services", 5, "Local cleaning and maintenance companies"),
    ("Landscaping Services", 5, "Local landscaping and lawn care businesses"),
    ("Pet Services", 7, "Pet stores, grooming, and boarding facilities"),
    ("Artisan Workshops", 6, "Local craftsmen and artisans"),
    ("Food Production", 7, "Local food producers and bakeries"),
    ("Photography Studios", 7, "Local photography businesses"),
    ("Interior Design Firms", 8, "Small interior design studios"),
    ("Marketing Agencies", 9, "Small marketing and advertising firms")
]

def get_existing_sites() -> Dict:
    """Fetch existing sites from Firebase"""
    print("Fetching existing sites from Firebase...")
    
    firebase_url = "https://emailsender-44bcc-default-rtdb.firebaseio.com/siteList.json"
    
    try:
        response = requests.get(firebase_url)
        if response.status_code == 200:
            sites = response.json() or {}
            print(f"Found {len(sites)} existing sites")
            return sites
        else:
            print(f"Failed to fetch existing sites: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error fetching existing sites: {str(e)}")
        return {}

def get_existing_business_names(sites: Dict) -> Set[str]:
    """Extract business names from existing sites"""
    business_names = set()
    for site_data in sites.values():
        if isinstance(site_data, dict) and 'name' in site_data:
            business_names.add(site_data['name'].lower().strip())
    return business_names

def get_businesses_from_grok(city: str, state: str, business_type: str, description: str, 
                           software_probability: int, existing_names: Set[str]) -> List[Dict]:
    """Get business information from Grok API for a specific business type in a city"""
    print(f"Getting business information for {business_type} in {city}, {state}")
    
    # Prepare the request to Grok API
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer xai-S375bT9UgdT3qzjhXHO88F3WHbmGgZzlzJMbw05d9Bkv3s6cGwZcM3fff40fb7j8gi9xgLpmnrgSurmE"
    }
    
    existing_names_list = list(existing_names)
    query = f"""Find 5 SMALL businesses in {city}, {state} that are {business_type}.
    {description}
    
    DO NOT include any of these existing businesses: {existing_names_list}
    
    IMPORTANT CRITERIA:
    - Must be a small business with 1-100 employees
    - Should be independently owned and operated
    - Should be a local business, not a national chain
    - Annual revenue should typically be under $10 million
    - Should be a single location or have very few locations
    - Should be a business that could benefit from personalized outreach
    - Should NOT be highly technical or already have sophisticated software solutions
    
    For each business, provide:
    1. Business Name
    2. Email Address
    3. Website URL
    4. Brief Description of what the business does
    5. Estimated number of employees (1-100)
    6. Technical sophistication analysis:
       - Current level of technology use
       - Potential areas for software improvement
       - Why they might need custom software solutions
    7. Business analysis:
       - Why they qualify as a small business
       - Their potential for growth
       - How custom software could benefit them
    
    Format the response as a JSON array of objects with these fields:
    [
        {{
            "name": "Business Name",
            "email": "email@example.com",
            "website": "https://example.com",
            "description": "Brief description",
            "employee_count": "Estimated number (1-100)",
            "technical_analysis": {{
                "current_tech_level": "Description of current technology use",
                "improvement_areas": "Areas where software could help",
                "software_needs": "Why they need custom software"
            }},
            "business_analysis": {{
                "small_business_qualification": "Why they qualify as small",
                "growth_potential": "Potential for growth",
                "software_benefits": "How software could help"
            }}
        }}
    ]
    
    IMPORTANT: Respond ONLY with the JSON array, no additional text or explanation."""
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a business research assistant specializing in finding small, independently owned businesses that could benefit from custom software solutions. Focus on businesses with 1-100 employees that are local or regional in scope and not highly technical. Provide accurate and up-to-date business information in JSON format. Respond ONLY with the JSON array, no additional text."
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "model": "grok-2-latest",
        "stream": False,
        "temperature": 0
    }
    
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Grok API returned non-200 status code: {response.status_code}")
            print(f"Response text: {response.text}")
            return []
        
        response_json = response.json()
        content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "[]")
        
        print(f"Raw response from Grok: {content}")
        
        try:
            # Clean the content string to ensure it's valid JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse the JSON string from Grok's response
            businesses = json.loads(content)
            
            # Validate the structure
            if not isinstance(businesses, list):
                print("Response is not a list of businesses")
                return []
                
            # Validate each business entry and check for duplicates
            valid_businesses = []
            for business in businesses:
                required_fields = ["name", "email", "website", "description", "employee_count", 
                                 "technical_analysis", "business_analysis"]
                if all(key in business for key in required_fields):
                    # Check if business name already exists
                    if business['name'].lower().strip() not in existing_names:
                        # Additional validation for small business criteria
                        description = business['description'].lower()
                        if any(term in description for term in ['small', 'local', 'family-owned', 'independent', 'boutique']):
                            # Validate employee count
                            try:
                                emp_count = int(business['employee_count'])
                                if 1 <= emp_count <= 100:
                                    # Add software probability score
                                    business['software_probability'] = software_probability
                                    business['city'] = city
                                    business['state'] = state
                                    business['business_type'] = business_type
                                    valid_businesses.append(business)
                                else:
                                    print(f"Skipping business with invalid employee count: {business['name']}")
                            except ValueError:
                                print(f"Skipping business with invalid employee count format: {business['name']}")
                        else:
                            print(f"Skipping business that doesn't meet small business criteria: {business['name']}")
                    else:
                        print(f"Skipping duplicate business: {business['name']}")
                else:
                    print(f"Invalid business entry: {business}")
            
            return valid_businesses
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse Grok response as JSON: {str(e)}")
            print(f"Content that failed to parse: {content}")
            return []
            
    except Exception as e:
        print(f"Error making request to Grok API: {str(e)}")
        return []

def save_to_firebase(businesses: List[Dict], city: str, state: str, business_type: str):
    """Save business data to Firebase Realtime Database"""
    print(f"Saving {len(businesses)} businesses to Firebase for {business_type} in {city}, {state}")
    
    success_count = 0
    for business in businesses:
        try:
            # Clean business name for use in key
            clean_name = ''.join(c for c in business['name'] if c.isalnum() or c.isspace())
            clean_name = clean_name.replace(' ', '_')
            
            # Clean and validate all text fields
            cleaned_business = {
                'name': business['name'].strip(),
                'email': business['email'].strip().lower(),
                'website': business['website'].strip(),
                'description': business['description'].strip(),
                'city': city.strip(),
                'state': state.strip(),
                'business_type': business_type.strip(),
                'software_probability': business['software_probability'],
                'employee_count': business['employee_count'],
                'technical_analysis': {
                    'current_tech_level': business['technical_analysis']['current_tech_level'].strip(),
                    'improvement_areas': business['technical_analysis']['improvement_areas'].strip(),
                    'software_needs': business['technical_analysis']['software_needs'].strip()
                },
                'business_analysis': {
                    'small_business_qualification': business['business_analysis']['small_business_qualification'].strip(),
                    'growth_potential': business['business_analysis']['growth_potential'].strip(),
                    'software_benefits': business['business_analysis']['software_benefits'].strip()
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Save each business to its own path
            firebase_url = f"https://emailsender-44bcc-default-rtdb.firebaseio.com/siteList/{clean_name}.json"
            
            # Send data to Firebase
            firebase_response = requests.put(firebase_url, json=cleaned_business)
            
            if firebase_response.status_code == 200:
                success_count += 1
            else:
                print(f"Failed to save business {clean_name}: {firebase_response.status_code}")
                print(f"Response text: {firebase_response.text}")
            
        except Exception as e:
            print(f"Error saving business {business.get('name', 'unknown')}: {str(e)}")
    
    print(f"Successfully saved {success_count} out of {len(businesses)} businesses to Firebase")
    return success_count > 0

def main():
    print("Business Information Scraper using Grok")
    print("=" * 50)
    
    # Get existing sites first
    existing_sites = get_existing_sites()
    existing_names = get_existing_business_names(existing_sites)
    
    # Randomly select 5 cities and 5 business types
    selected_cities = random.sample(MAJOR_CITIES, 5)
    selected_business_types = random.sample(BUSINESS_TYPES, 5)
    
    for city, state in selected_cities:
        for business_type, software_probability, description in selected_business_types:
            print(f"\nProcessing {business_type} in {city}, {state}")
            businesses = get_businesses_from_grok(city, state, business_type, description, 
                                               software_probability, existing_names)
            
            if businesses:
                success = save_to_firebase(businesses, city, state, business_type)
                if success:
                    # Update existing names with newly added businesses
                    for business in businesses:
                        existing_names.add(business['name'].lower().strip())
                    print(f"Successfully processed {business_type} in {city}, {state}")
                else:
                    print(f"Failed to save data for {business_type} in {city}, {state}")
            else:
                print(f"No businesses found for {business_type} in {city}, {state}")
            
            print("-" * 50)
    
    print("\nScraping completed!")

if __name__ == "__main__":
    main() 