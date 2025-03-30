#!/usr/bin/env python3
import requests
import json
import os
import random
from datetime import datetime
from typing import List, Dict, Set, Tuple

# Major cities from English-speaking countries
MAJOR_CITIES = [
    # United States
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
    
    # West Coast
    ("Los Angeles", "CA"),
    ("San Francisco", "CA"),
    ("Seattle", "WA"),
    ("Portland", "OR"),
    ("San Diego", "CA"),
    
    # Canada
    # Ontario
    ("Toronto", "ON"),
    ("Ottawa", "ON"),
    ("Hamilton", "ON"),
    ("London", "ON"),
    ("Windsor", "ON"),
    
    # Quebec
    ("Montreal", "QC"),
    ("Quebec City", "QC"),
    
    # British Columbia
    ("Vancouver", "BC"),
    ("Victoria", "BC"),
    ("Surrey", "BC"),
    
    # Alberta
    ("Calgary", "AB"),
    ("Edmonton", "AB"),
    
    # Other Canadian Cities
    ("Winnipeg", "MB"),
    ("Halifax", "NS"),
    ("St. John's", "NL"),
    
    # United Kingdom
    # England
    ("London", "England"),
    ("Manchester", "England"),
    ("Birmingham", "England"),
    ("Leeds", "England"),
    ("Liverpool", "England"),
    ("Bristol", "England"),
    ("Sheffield", "England"),
    ("Newcastle", "England"),
    ("Nottingham", "England"),
    ("Leicester", "England"),
    
    # Scotland
    ("Edinburgh", "Scotland"),
    ("Glasgow", "Scotland"),
    ("Aberdeen", "Scotland"),
    ("Dundee", "Scotland"),
    
    # Wales
    ("Cardiff", "Wales"),
    ("Swansea", "Wales"),
    
    # Northern Ireland
    ("Belfast", "Northern Ireland"),
    ("Derry", "Northern Ireland"),
    
    # Ireland
    ("Dublin", "Ireland"),
    ("Cork", "Ireland"),
    ("Limerick", "Ireland"),
    ("Galway", "Ireland"),
    ("Waterford", "Ireland"),
    
    # Australia
    # New South Wales
    ("Sydney", "NSW"),
    ("Newcastle", "NSW"),
    ("Wollongong", "NSW"),
    
    # Victoria
    ("Melbourne", "VIC"),
    ("Geelong", "VIC"),
    ("Ballarat", "VIC"),
    
    # Queensland
    ("Brisbane", "QLD"),
    ("Gold Coast", "QLD"),
    ("Townsville", "QLD"),
    
    # Western Australia
    ("Perth", "WA"),
    ("Fremantle", "WA"),
    
    # South Australia
    ("Adelaide", "SA"),
    
    # Tasmania
    ("Hobart", "TAS"),
    ("Launceston", "TAS"),
    
    # New Zealand
    ("Auckland", "NZ"),
    ("Wellington", "NZ"),
    ("Christchurch", "NZ"),
    ("Hamilton", "NZ"),
    ("Tauranga", "NZ"),
    
    # South Africa
    ("Cape Town", "WC"),
    ("Johannesburg", "GP"),
    ("Durban", "KZN"),
    ("Pretoria", "GP"),
    ("Port Elizabeth", "EC"),
    
    # Singapore
    ("Singapore", "SG"),
    
    # Hong Kong
    ("Hong Kong", "HK"),
    
    # India (Major English-speaking cities)
    ("Mumbai", "MH"),
    ("Delhi", "DL"),
    ("Bangalore", "KA"),
    ("Chennai", "TN"),
    ("Hyderabad", "TG"),
    
    # Philippines (Major English-speaking cities)
    ("Manila", "PH"),
    ("Cebu City", "PH"),
    ("Davao City", "PH"),
    ("Quezon City", "PH"),
    
    # Malaysia (Major English-speaking cities)
    ("Kuala Lumpur", "MY"),
    ("Penang", "MY"),
    ("Johor Bahru", "MY"),
    
    # UAE (Major English-speaking cities)
    ("Dubai", "AE"),
    ("Abu Dhabi", "AE"),
    ("Sharjah", "AE")
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
    ("Marketing Agencies", 9, "Small marketing and advertising firms"),
    
    # Additional business types
    ("E-commerce Stores", 9, "Online businesses selling goods or services"),
    ("Consulting Firms", 8, "Small consulting companies"),
    ("Non-Profit Organizations", 7, "Non-profit and charity organizations"),
    ("Construction Materials Suppliers", 7, "Suppliers of materials for the construction industry"),
    ("Transportation Services", 6, "Local transport and logistics businesses"),
    ("Insurance Agencies", 8, "Local or small insurance firms"),
    ("Home Services", 6, "Home repair and improvement businesses"),
    ("IT Support Services", 8, "Businesses providing IT services and support"),
    ("Travel Agencies", 7, "Small travel agencies"),
    ("Digital Product Creators", 9, "Businesses selling digital products or services"),
    ("Fitness Equipment Suppliers", 6, "Companies selling fitness equipment"),
    ("Security Services", 7, "Local security firms providing installation and monitoring"),
    ("Real Estate Developers", 8, "Companies involved in property development"),
    ("Health and Wellness Coaches", 7, "Personal coaching services in wellness and fitness"),
    ("Luxury Goods Providers", 7, "Retailers of high-end, specialty products"),
    ("Craft Breweries", 7, "Small businesses specializing in craft beer production"),
    ("Specialty Food Stores", 8, "Retailers of gourmet or specialty foods"),
    ("Event Venues", 8, "Business venues offering space for events and gatherings"),
    ("Tech Startups", 9, "Innovative small tech companies in various industries"),
    ("Social Media Influencers", 7, "Individuals or agencies managing social media campaigns"),
    ("SaaS Companies", 10, "Software as a Service companies developing platforms or applications"),
    ("Freelancers & Creative Professionals", 6, "Individuals or agencies offering freelance services like writing, design, etc."),
    ("Public Relations Firms", 8, "Companies specializing in media relations and brand management"),
    ("Recruitment Agencies", 7, "Small businesses helping companies find and hire talent"),
    ("Mobile App Developers", 9, "Businesses developing mobile applications"),
    ("Cybersecurity Firms", 8, "Companies focused on providing cybersecurity solutions"),
    ("3D Printing Services", 7, "Businesses offering 3D printing solutions for various industries"),
    ("Subscription Box Services", 8, "E-commerce businesses offering subscription box products"),
    ("Tech Support Startups", 7, "Small tech support businesses"),
    ("Personalized Goods Providers", 7, "Companies offering customizable or personalized products"),
    ("Game Development Studios", 9, "Businesses developing video games or interactive media"),
    ("Online Education Platforms", 9, "Companies offering online courses or educational materials"),
    
    # Niche and emerging businesses
    ("Aquarium Services", 6, "Businesses offering aquarium setup and maintenance"),
    ("Drones and UAV Services", 8, "Companies offering drone-related services like surveying or aerial photography"),
    ("Urban Farming", 7, "Small businesses involved in urban agriculture or hydroponic farming"),
    ("Virtual Reality Studios", 9, "Businesses creating VR content or applications"),
    ("Sustainable Product Brands", 7, "Eco-friendly product companies or sustainability-focused businesses"),
    ("Mobile Car Wash Services", 6, "Mobile businesses offering car washing and detailing"),
    ("Home Staging Companies", 7, "Businesses that stage homes for sale"),
    ("Antique Dealers", 6, "Small businesses specializing in antique sales and restoration"),
    ("Specialty Coffee Roasters", 7, "Local coffee roasters and distributors"),
    ("Comic Book Shops", 6, "Retailers specializing in comic book sales and collectibles"),
    ("Tiny House Builders", 7, "Businesses building and selling tiny homes"),
    ("Furniture Restoration", 6, "Companies specializing in the restoration of vintage furniture"),
    ("Co-Working Spaces", 7, "Shared workspaces for freelancers and small businesses"),
    ("Urban Planners", 7, "Companies providing urban design and planning services"),
    ("Escape Rooms", 6, "Entertainment venues offering escape room experiences"),
    ("Pet Training Services", 6, "Businesses offering dog or pet training and behavioral services"),
    ("Custom Apparel Designers", 7, "Small businesses focused on custom clothing design and production"),
    ("Mobile Repair Services", 6, "Businesses providing repair services at the customer's location"),
    ("Nail Salons", 5, "Local businesses specializing in nail care and art"),
    ("Personal Stylists", 6, "Freelance or boutique businesses offering styling services"),
    ("Tattoo Studios", 6, "Local businesses providing tattoo design and artistry"),
    ("Laser Tag Arenas", 5, "Entertainment venues offering laser tag experiences"),
    ("Food Trucks", 7, "Mobile food service businesses specializing in unique offerings"),
    ("Mobile Health Clinics", 7, "Mobile services providing healthcare to underserved areas"),
    ("Environmental Consulting", 8, "Consulting firms offering environmental and sustainability advice"),
    ("Bicycle Repair Shops", 5, "Local businesses offering bicycle maintenance and repair"),
    ("3D Animation Studios", 8, "Companies providing animation services for film, gaming, and marketing"),
    ("Virtual Assistants", 6, "Freelance services offering administrative assistance remotely"),
    ("Smart Home Installation", 7, "Companies providing smart home and automation installation services"),
    ("Film Production Studios", 8, "Small businesses focused on independent film production"),
    ("Voice Over Artists", 6, "Freelance or small businesses offering voice-over services"),
    ("Personal Chefs", 6, "Freelancers offering customized meal preparation and private cooking services"),
    ("Candle Makers", 5, "Small businesses producing hand-made or specialty candles"),
    ("Outdoor Adventure Guides", 7, "Small companies offering outdoor experiences or adventure tours"),
    ("Self-Publishing Services", 6, "Businesses that assist in the self-publishing of books and media"),
    ("Elderly Care Providers", 7, "Businesses focused on in-home healthcare for elderly clients"),
    
    # Legacy businesses with outdated software
    ("Accounting Firms", 9, "Firms providing accounting and bookkeeping services, often using legacy accounting software"),
    ("Wholesale Distributors", 8, "Businesses in wholesale distribution that may rely on older inventory and order management systems"),
    ("Car Dealerships", 8, "Dealerships with outdated inventory and customer relationship management software"),
    ("Publishing Houses", 8, "Publishers of books, newspapers, or magazines with legacy editing, design, and distribution systems"),
    ("Printing Presses", 7, "Printing companies with legacy job tracking and production management systems"),
    ("Utilities Companies", 9, "Companies providing essential services such as water, electricity, and gas, often with legacy infrastructure management systems"),
    ("Pharmacies", 8, "Long-standing pharmacies with outdated patient management and inventory systems"),
    ("Law Enforcement Agencies", 9, "Public safety departments with legacy records management and communication systems"),
    ("Public Libraries", 8, "Libraries with older cataloging and borrowing systems"),
    ("Real Estate Investment Firms", 8, "Established firms managing real estate portfolios with outdated property tracking systems"),
    ("Hotels & Inns", 8, "Hospitality businesses with outdated booking, reservation, and property management software"),
    ("Dry Cleaners", 7, "Long-established dry cleaning businesses with legacy inventory tracking and order management systems"),
    ("Agricultural Cooperatives", 8, "Old cooperatives for farming or agriculture with outdated inventory and member management software"),
    ("Telecommunications Companies", 9, "Telecom providers with outdated billing and customer service systems"),
    ("Auto Insurance Firms", 9, "Insurance companies focused on auto insurance with legacy claims and policy management systems"),
    ("Financial Advisors", 8, "Financial advisory firms using older portfolio management and client relationship software"),
    ("Furniture Retailers", 8, "Retailers with outdated point-of-sale and inventory management systems"),
    
    # Emerging and innovative businesses
    ("Virtual Event Platforms", 9, "Businesses offering virtual event hosting and management tools"),
    ("Biotechnology Startups", 9, "Companies working in biotech and pharmaceutical innovations"),
    ("Smart Agriculture", 8, "Farming businesses utilizing smart technology for agriculture"),
    ("Pop-Up Retail Shops", 7, "Temporary retail shops, often focused on seasonal sales"),
    ("Mobile Fitness Trainers", 7, "Freelancers or small businesses providing on-the-go fitness services"),
    ("Online Marketplace Platforms", 9, "Businesses creating platforms for buying and selling products online"),
    ("Aquatic Therapy Centers", 8, "Therapy businesses utilizing water-based treatment methods"),
    ("Voice Recognition Services", 8, "Companies offering voice-to-text or speech recognition software"),
    ("Personalized Nutrition Services", 7, "Businesses offering custom dietary planning and nutrition consultations"),
    ("Green Energy Consulting", 8, "Firms providing advisory services for sustainable energy solutions"),
    ("Custom Drone Services", 8, "Businesses specializing in drone-based services like mapping or delivery"),
    ("Luxury Car Rentals", 7, "High-end vehicle rental services"),
    ("On-Demand Delivery Services", 8, "Businesses offering fast delivery of goods and services"),
    ("Digital Artists & Illustrators", 6, "Freelance digital artists or small design studios"),
    ("Mobile Beauty Services", 7, "Freelancers providing beauty services at clients' locations"),
    ("Bespoke Tailoring Services", 6, "Custom clothing designers providing tailored fashion"),
    ("Vape Shops", 6, "Retail businesses selling vape products and accessories"),
    ("Sustainable Fashion Brands", 7, "Eco-conscious fashion brands focusing on sustainability"),
    ("Subscription-Based Food Services", 8, "Food delivery services offering subscription-based meal plans"),
    ("Gaming Cafes", 7, "Cafes with high-end gaming PCs and gaming-focused services"),
    ("Smart Wearables", 8, "Businesses developing or selling wearable technology"),
    ("Crowdfunding Platforms", 9, "Platforms facilitating crowdfunding for projects and startups"),
    ("Urban Transportation Solutions", 7, "Services offering solutions for urban mobility like e-scooters or shared bikes"),
    ("Craft Distilleries", 7, "Small, artisanal distilleries producing craft spirits"),
    ("Sustainable Packaging Solutions", 8, "Businesses providing eco-friendly packaging alternatives"),
    ("Health & Fitness Apps", 9, "Mobile applications focused on health, wellness, and fitness"),
    ("Cloud Kitchens", 8, "Restaurants that operate exclusively through delivery services without physical dining spaces"),
    ("Cryptocurrency Platforms", 9, "Platforms offering trading, storage, or services related to cryptocurrencies"),
    ("Local Art Galleries", 6, "Small businesses showcasing and selling local or contemporary art"),
    ("DIY Craft Subscription Boxes", 7, "Subscription services providing craft kits and DIY projects"),
    ("Talent Agencies", 7, "Agencies representing actors, models, or other professionals"),
    ("Independent Publishers", 7, "Small-scale publishers specializing in niche markets or independent works"),
    ("Remote Team Collaboration Tools", 9, "Software businesses focused on remote team management and collaboration solutions"),
    ("Virtual Reality Fitness", 9, "Fitness businesses offering virtual reality-based workout experiences"),
    ("Crowdsourced Translation Services", 8, "Platforms offering translation services via crowdsourcing"),
    ("NFT Marketplace Platforms", 9, "Platforms that support buying and selling NFTs (Non-Fungible Tokens)"),
    ("Pet Adoption Platforms", 7, "Online platforms connecting pet owners with adoptable animals"),
    ("Microgreens Farming", 7, "Small-scale farming businesses focused on growing microgreens"),
    ("Personalized Gifts", 6, "Retail businesses offering custom or personalized gift products"),
    ("Senior Living Communities", 8, "Businesses providing services and management for senior living facilities"),
    ("B2B Supply Chain Solutions", 9, "Platforms offering business-to-business supply chain management tools"),
    ("Custom Furniture Designers", 7, "Businesses focused on creating bespoke furniture pieces"),
    ("Nutraceuticals", 7, "Companies involved in producing supplements and functional foods")
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