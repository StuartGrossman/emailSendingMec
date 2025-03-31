#!/usr/bin/env python3
import requests
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import time
import argparse
import random
import concurrent.futures
import os
from src.config.config import (
    GROK_API_KEY,
    GROK_API_KEY_2,
    GROK_API_KEY_3,
    GROK_API_KEY_4,
    REQUEST_TIMEOUT,
    LOG_LEVEL,
    LOG_FILE,
    FIREBASE_URL,
    GOOGLE_PLACES_API_KEY,
    DEEPSEEK_API_KEY,
    MIN_RATING,
    MIN_REVIEWS
)
from src.scrapers.business_scraper import MAJOR_CITIES, BUSINESS_TYPES

# Update MAJOR_CITIES to focus on American cities
MAJOR_CITIES = [
    ("New York", "NY"),
    ("Los Angeles", "CA"),
    ("Chicago", "IL"),
    ("Houston", "TX"),
    ("Phoenix", "AZ"),
    ("Philadelphia", "PA"),
    ("San Antonio", "TX"),
    ("San Diego", "CA"),
    ("Dallas", "TX"),
    ("San Jose", "CA"),
    ("Austin", "TX"),
    ("Jacksonville", "FL"),
    ("Fort Worth", "TX"),
    ("Columbus", "OH"),
    ("San Francisco", "CA"),
    ("Charlotte", "NC"),
    ("Indianapolis", "IN"),
    ("Seattle", "WA"),
    ("Denver", "CO"),
    ("Washington", "DC"),
    ("Boston", "MA"),
    ("Nashville", "TN"),
    ("Portland", "OR"),
    ("Miami", "FL"),
    ("Atlanta", "GA"),
    ("Minneapolis", "MN"),
    ("New Orleans", "LA"),
    ("Cleveland", "OH"),
    ("Detroit", "MI"),
    ("Las Vegas", "NV")
]

# Update BUSINESS_TYPES to match our target business types
BUSINESS_TYPES = [
    ("Local Restaurants", "Restaurants with outdated POS systems or manual operations"),
    ("Small Manufacturing Companies", "Manufacturers using legacy ERP systems"),
    ("Local Retail Stores", "Retailers with outdated inventory management"),
    ("Small Healthcare Practices", "Medical practices using legacy practice management software"),
    ("Local Construction Companies", "Construction firms with outdated project management tools"),
    ("Small Accounting Firms", "Accounting firms using legacy accounting software"),
    ("Local Real Estate Agencies", "Real estate agencies with outdated CRM systems"),
    ("Small Law Firms", "Law firms using legacy case management software"),
    ("Local Insurance Agencies", "Insurance agencies with outdated policy management systems"),
    ("Small Educational Institutions", "Schools using legacy student management systems"),
    ("Local Auto Repair Shops", "Auto repair shops with outdated service management software"),
    ("Small Dental Practices", "Dental practices using legacy practice management software"),
    ("Local HVAC Companies", "HVAC companies with outdated service management systems"),
    ("Small Plumbing Companies", "Plumbing companies with outdated scheduling software"),
    ("Local Moving Companies", "Moving companies with outdated logistics software")
]

class PhoneLeadScraper:
    def __init__(self, grok_api_keys: List[str]):
        """Initialize the phone lead scraper with multiple API keys."""
        self.grok_api_keys = grok_api_keys
        self.current_key_index = 0
        self.google_headers = {
            "Content-Type": "application/json"
        }
        self.deepseek_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        self.grok_headers_list = [
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {key}"
            }
            for key in grok_api_keys
        ]
        self.logger = self._setup_logger()
        
        # Store Firebase URL
        self.firebase_url = FIREBASE_URL.rstrip('/')
        
        # Define business categories and their characteristics
        self.business_categories = {
            business_type[0].lower().replace(" ", "_"): {
                "keywords": [business_type[0]],
                "tech_indicators": ["scheduling system", "inventory management", "customer database", "POS system"],
                "pain_points": ["appointment scheduling", "inventory tracking", "customer communication", "work order management"]
            }
            for business_type in BUSINESS_TYPES
        }

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the scraper."""
        logger = logging.getLogger('PhoneLeadScraper')
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        if not logger.handlers:
            handler = logging.FileHandler(LOG_FILE)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            # Also log to console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger

    def _get_next_grok_headers(self):
        """Get the next Grok API headers in a round-robin fashion."""
        headers = self.grok_headers_list[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.grok_headers_list)
        return headers

    def _make_grok_request(self, endpoint: str, payload: Dict) -> Optional[Dict]:
        """Make a request to Grok API with automatic retry and key rotation."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = self._get_next_grok_headers()
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=REQUEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Grok API error: {response.status_code}")
                    self.logger.error(f"Response: {response.text}")
                    return None
                    
            except Exception as e:
                self.logger.error(f"Error making Grok request: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return None
        return None

    def _analyze_business_with_grok(self, business_info: Dict, category_info: Dict) -> Dict:
        """Use Grok to analyze a business and determine if it's a good candidate for custom software."""
        try:
            prompt = f"""Analyze this business as a potential client for custom software development services. IMPORTANT: Only analyze information that is explicitly provided in the business information. Do not make assumptions or add information that is not present in the input data.

Business Information:
{json.dumps(business_info, indent=2)}

Category Information:
Tech Indicators: {json.dumps(category_info['tech_indicators'])}
Pain Points: {json.dumps(category_info['pain_points'])}

Rules for Analysis:
1. Only use information explicitly provided in the business information
2. Do not make assumptions about systems or processes not mentioned
3. If a piece of information is not provided, mark it as "Not specified" or use an empty list
4. Scores must be based only on available information
5. Do not invent or hallucinate any details about the business

You must respond with a valid JSON object containing the following sections:

{{
    "tech_stack": {{
        "current_systems": ["list of systems explicitly mentioned"],
        "system_age": "description based on available information",
        "limitations": ["list of limitations mentioned"],
        "integration_challenges": ["list of challenges mentioned"],
        "score": number between 1-10 based on available information
    }},
    "operations": {{
        "scale": "description based on employee count",
        "complexity": "description based on available information",
        "efficiency_level": "description based on available information",
        "manual_processes": ["list of processes mentioned"],
        "score": number between 1-10 based on available information
    }},
    "growth_potential": {{
        "market_position": "description based on available information",
        "growth_indicators": ["list of indicators mentioned"],
        "tech_readiness": "description based on available information",
        "score": number between 1-10 based on available information
    }},
    "software_opportunity": {{
        "pain_points": ["list of pain points mentioned"],
        "roi_areas": ["list of ROI areas based on available information"],
        "integration_requirements": ["list of requirements mentioned"],
        "score": number between 1-10 based on available information
    }},
    "decision_maker": {{
        "stakeholders": ["list of stakeholders mentioned"],
        "investment_signals": ["list of signals mentioned"],
        "contact_approach": "description based on available information",
        "score": number between 1-10 based on available information
    }},
    "sales_conversation": {{
        "opening_points": ["list of points based on available information"],
        "pain_points_to_discuss": ["list of points mentioned"],
        "roi_examples": ["list of examples based on available information"],
        "solutions_to_propose": ["list of solutions based on available information"],
        "questions_to_ask": ["list of questions based on available information"]
    }}
}}

Make the analysis actionable for a sales conversation. Each section must be present and contain the specified fields.
"""

            response = self._make_grok_request(
                "https://api.x.ai/v1/chat/completions",
                {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a business technology analyst specializing in identifying opportunities for custom software solutions. Provide detailed, actionable insights for sales conversations. Always respond with valid JSON matching the exact structure specified in the prompt."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": "grok-2",
                    "temperature": 0.7,
                    "max_tokens": 1500
                }
            )
            
            if response:
                try:
                    analysis = response["choices"][0]["message"]["content"]
                    # Clean up the response to ensure it's valid JSON
                    analysis = analysis.strip()
                    if not analysis.startswith('{'):
                        analysis = analysis[analysis.find('{'):]
                    if not analysis.endswith('}'):
                        analysis = analysis[:analysis.rfind('}')+1]
                    
                    parsed_analysis = json.loads(analysis)
                    
                    # Validate required fields and data types
                    required_sections = [
                        "tech_stack", "operations", "growth_potential",
                        "software_opportunity", "decision_maker", "sales_conversation"
                    ]
                    
                    for section in required_sections:
                        if section not in parsed_analysis:
                            self.logger.error(f"Missing required section: {section}")
                            return {}
                        
                        # Validate scores are numbers between 1-10
                        if "score" in parsed_analysis[section]:
                            score = parsed_analysis[section]["score"]
                            if not isinstance(score, (int, float)) or score < 1 or score > 10:
                                self.logger.error(f"Invalid score in {section}: {score}")
                                return {}
                    
                    # Validate lists are actually lists
                    for section in parsed_analysis:
                        for key, value in parsed_analysis[section].items():
                            if isinstance(value, list):
                                if not all(isinstance(item, str) for item in value):
                                    self.logger.error(f"Invalid list items in {section}.{key}")
                                    return {}
                    
                    return parsed_analysis
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse Grok analysis as JSON: {str(e)}")
                    self.logger.error(f"Raw response: {analysis}")
                    return {}
            else:
                self.logger.error("Grok analysis failed")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error during business analysis: {str(e)}")
            return {}

    def _fetch_real_businesses(self, city: str, state: str, business_type: str) -> List[Dict]:
        """Fetch real business data from Google Places API."""
        try:
            # Format the search query
            query = f"{business_type} in {city}, {state}"
            
            # First, get place IDs
            search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query,
                "key": GOOGLE_PLACES_API_KEY
            }
            
            response = requests.get(search_url, params=params, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                self.logger.error(f"Google Places search failed: {response.status_code}")
                return []
                
            places = response.json().get("results", [])
            businesses = []
            
            for place in places:
                # Only consider highly-rated businesses
                rating = place.get("rating", 0)
                reviews = place.get("user_ratings_total", 0)
                
                if rating >= MIN_RATING and reviews >= MIN_REVIEWS:
                    # Get detailed place information
                    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                    details_params = {
                        "place_id": place["place_id"],
                        "fields": "name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,reviews",
                        "key": GOOGLE_PLACES_API_KEY
                    }
                    
                    details_response = requests.get(details_url, params=details_params, timeout=REQUEST_TIMEOUT)
                    if details_response.status_code == 200:
                        details = details_response.json().get("result", {})
                        
                        business = {
                            "name": details.get("name", ""),
                            "phone": details.get("formatted_phone_number", ""),
                            "address": details.get("formatted_address", ""),
                            "website": details.get("website", ""),
                            "description": f"{business_type} in {city}",
                            "rating": rating,
                            "reviews": reviews,
                            "recent_reviews": [
                                {
                                    "text": review.get("text", ""),
                                    "rating": review.get("rating", 0),
                                    "time": review.get("relative_time_description", "")
                                }
                                for review in details.get("reviews", [])[:5]  # Get last 5 reviews
                            ]
                        }
                        businesses.append(business)
                        
                        # Rate limit to avoid hitting API limits
                        time.sleep(0.5)
            
            return businesses
            
        except Exception as e:
            self.logger.error(f"Error fetching businesses from Google Places: {str(e)}")
            return []

    def _validate_with_deepseek(self, business: Dict, analysis: Dict) -> Dict:
        """Validate business data and analysis using DeepSeek."""
        try:
            prompt = f"""Validate this business lead and its analysis for accuracy and potential. The business data comes from real website analysis.

Business Information:
{json.dumps(business, indent=2)}

Current Analysis:
{json.dumps(analysis, indent=2)}

IMPORTANT: You must respond with a valid JSON object. Do not include any text before or after the JSON object.

Validate and provide:
1. Whether this is a legitimate business opportunity (based on website and analysis)
2. The accuracy of the current analysis
3. Any red flags or inconsistencies
4. Confidence score (0-100) in this lead

Respond with this exact JSON structure:

{{
    "is_legitimate": boolean,
    "confidence_score": number between 0-100,
    "validation_points": [
        "point 1",
        "point 2",
        ...
    ],
    "red_flags": [
        "flag 1",
        "flag 2",
        ...
    ],
    "analysis_accuracy": {{
        "tech_stack": number between 0-100,
        "operations": number between 0-100,
        "growth_potential": number between 0-100,
        "software_opportunity": number between 0-100
    }},
    "recommendation": "proceed" | "investigate" | "reject"
}}

Example response:
{{
    "is_legitimate": true,
    "confidence_score": 85,
    "validation_points": [
        "Website confirms business size and operations",
        "Technology needs clearly visible",
        "Growth indicators present"
    ],
    "red_flags": [
        "Recent negative reviews",
        "Unclear decision-making structure"
    ],
    "analysis_accuracy": {{
        "tech_stack": 90,
        "operations": 85,
        "growth_potential": 80,
        "software_opportunity": 85
    }},
    "recommendation": "proceed"
}}

Provide ONLY the JSON object, nothing else."""

            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=self.deepseek_headers,
                json={
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a business validation expert specializing in verifying sales leads and opportunities. Always respond with valid JSON objects matching the exact structure specified."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": "deepseek-chat",
                    "temperature": 0.3
                },
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                try:
                    content = response.json()["choices"][0]["message"]["content"]
                    # Clean up the response to ensure it's valid JSON
                    content = content.strip()
                    if not content.startswith('{'):
                        content = content[content.find('{'):]
                    if not content.endswith('}'):
                        content = content[:content.rfind('}')+1]
                    
                    validation = json.loads(content)
                    
                    # Validate required fields
                    required_fields = [
                        "is_legitimate", "confidence_score", "validation_points",
                        "red_flags", "analysis_accuracy", "recommendation"
                    ]
                    
                    if not all(field in validation for field in required_fields):
                        self.logger.error("Missing required fields in validation")
                        return {}
                        
                    # Validate analysis_accuracy structure
                    required_accuracy_fields = [
                        "tech_stack", "operations", "growth_potential", "software_opportunity"
                    ]
                    
                    if not all(field in validation["analysis_accuracy"] for field in required_accuracy_fields):
                        self.logger.error("Missing required fields in analysis_accuracy")
                        return {}
                    
                    return validation
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse DeepSeek validation as JSON: {str(e)}")
                    self.logger.error(f"Raw response: {content}")
                    return {}
            else:
                self.logger.error(f"DeepSeek validation failed: {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return {}

        except Exception as e:
            self.logger.error(f"Error during DeepSeek validation: {str(e)}")
            return {}

    def _search_businesses_with_grok(self, city: str, state: str, business_type: str) -> List[Dict]:
        """Use Grok to search for businesses and analyze their websites."""
        try:
            prompt = f"""Search for real, established {business_type} businesses in {city}, {state} that would be good candidates for custom software solutions.

IMPORTANT: You must respond with a valid JSON array containing business objects. Do not include any text before or after the JSON array.

Requirements for each business:
1. Must have a public website
2. Must be likely to need software solutions
3. Must have good online presence and reviews
4. Must not be too small or clearly unsuitable

For each business, provide this exact JSON structure:
{{
    "name": "Business name",
    "website": "https://example.com",
    "phone": "phone number if available",
    "address": "address if available",
    "description": "brief description",
    "software_needs": ["list of software needs identified"],
    "growth_indicators": ["list of growth indicators"],
    "tech_readiness": "assessment of tech readiness",
    "confidence_score": number between 1-10
}}

Example response format:
[
    {{
        "name": "Example Tech Solutions",
        "website": "https://exampletech.com",
        "phone": "(555) 123-4567",
        "address": "123 Tech Street, San Francisco, CA",
        "description": "Growing software development company with outdated project management systems",
        "software_needs": ["Modern project management", "Client portal", "Automated reporting"],
        "growth_indicators": ["Expanding team", "New service offerings", "Recent client wins"],
        "tech_readiness": "Using basic tools, ready to modernize",
        "confidence_score": 8
    }}
]

Search for businesses and return ONLY the JSON array, nothing else."""

            response = self._make_grok_request(
                "https://api.x.ai/v1/chat/completions",
                {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a business research expert specializing in identifying companies that need custom software solutions. You must always respond with valid JSON arrays containing business objects."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": "grok-2",
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )

            if response:
                try:
                    content = response["choices"][0]["message"]["content"]
                    # Clean up the response to ensure it's valid JSON
                    content = content.strip()
                    if not content.startswith('['):
                        content = content[content.find('['):]
                    if not content.endswith(']'):
                        content = content[:content.rfind(']')+1]
                    
                    businesses = json.loads(content)
                    
                    # Validate each business object
                    valid_businesses = []
                    for business in businesses:
                        if all(key in business for key in ["name", "website", "confidence_score"]):
                            if business.get("confidence_score", 0) >= 7:
                                valid_businesses.append(business)
                    
                    return valid_businesses
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse Grok business search results: {str(e)}")
                    self.logger.error(f"Raw response: {content}")
                    return []
            else:
                self.logger.error("Grok business search failed")
                return []

        except Exception as e:
            self.logger.error(f"Error during business search: {str(e)}")
            return []

    def _analyze_website_with_grok(self, business: Dict) -> Dict:
        """Use Grok to analyze a business's website in detail."""
        try:
            prompt = f"""Visit and analyze this business's website to identify software needs and opportunities.

Business Information:
{json.dumps(business, indent=2)}

IMPORTANT: You must respond with a valid JSON object. Do not include any text before or after the JSON object.

Visit their website and analyze:
1. Current technology stack (if visible)
2. Pain points and inefficiencies
3. Growth opportunities
4. Software needs
5. Decision maker information
6. Budget indicators

Respond with this exact JSON structure:

{{
    "tech_stack": {{
        "current_systems": ["list of systems identified on website"],
        "system_age": "assessment of system age based on website",
        "limitations": ["list of limitations found"],
        "integration_challenges": ["list of challenges identified"],
        "score": number between 1-10
    }},
    "operations": {{
        "scale": "description of business scale from website",
        "complexity": "description of operations complexity",
        "efficiency_level": "assessment of efficiency from website",
        "manual_processes": ["list of manual processes found"],
        "score": number between 1-10
    }},
    "growth_potential": {{
        "market_position": "description from website",
        "growth_indicators": ["list of indicators found"],
        "tech_readiness": "assessment from website",
        "score": number between 1-10
    }},
    "software_opportunity": {{
        "pain_points": ["list of pain points found"],
        "roi_areas": ["list of ROI areas identified"],
        "integration_requirements": ["list of requirements found"],
        "score": number between 1-10
    }},
    "decision_maker": {{
        "stakeholders": ["list of stakeholders found"],
        "investment_signals": ["list of signals found"],
        "contact_approach": "recommended approach based on website",
        "score": number between 1-10
    }},
    "sales_conversation": {{
        "opening_points": ["list of points from website"],
        "pain_points_to_discuss": ["list of points found"],
        "roi_examples": ["list of examples from website"],
        "solutions_to_propose": ["list of solutions based on findings"],
        "questions_to_ask": ["list of questions based on analysis"]
    }}
}}

Example response:
{{
    "tech_stack": {{
        "current_systems": ["Legacy CRM", "Manual scheduling system"],
        "system_age": "Systems appear to be 5+ years old based on interface screenshots",
        "limitations": ["No mobile access", "Limited automation"],
        "integration_challenges": ["Separate systems not connected", "Data silos"],
        "score": 4
    }},
    ...rest of the structure...
}}

Visit their website at {business['website']} and provide ONLY the JSON object, nothing else."""

            response = self._make_grok_request(
                "https://api.x.ai/v1/chat/completions",
                {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a business technology analyst specializing in identifying opportunities for custom software solutions. Visit websites and provide detailed analysis in JSON format only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": "grok-2",
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )

            if response:
                try:
                    content = response["choices"][0]["message"]["content"]
                    # Clean up the response to ensure it's valid JSON
                    content = content.strip()
                    if not content.startswith('{'):
                        content = content[content.find('{'):]
                    if not content.endswith('}'):
                        content = content[:content.rfind('}')+1]
                    
                    analysis = json.loads(content)
                    
                    # Validate required sections
                    required_sections = [
                        "tech_stack", "operations", "growth_potential",
                        "software_opportunity", "decision_maker", "sales_conversation"
                    ]
                    
                    if not all(section in analysis for section in required_sections):
                        self.logger.error("Missing required sections in analysis")
                        return {}
                        
                    return analysis
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse Grok website analysis: {str(e)}")
                    self.logger.error(f"Raw response: {content}")
                    return {}
            else:
                self.logger.error("Grok website analysis failed")
                return {}

        except Exception as e:
            self.logger.error(f"Error during website analysis: {str(e)}")
            return {}

    def _process_business_parallel(self, business: Dict, city: str, state: str, business_type: str) -> Optional[Dict]:
        """Process a single business in parallel."""
        try:
            # Analyze website with Grok
            analysis = self._analyze_website_with_grok(business)
            
            if analysis:
                # Validate with DeepSeek
                validation = self._validate_with_deepseek(business, analysis)
                
                if validation.get("is_legitimate", False) and validation.get("confidence_score", 0) >= 70:
                    # Calculate overall score
                    scores = [
                        analysis.get("tech_stack", {}).get("score", 0),
                        analysis.get("operations", {}).get("score", 0),
                        analysis.get("growth_potential", {}).get("score", 0),
                        analysis.get("software_opportunity", {}).get("score", 0),
                        analysis.get("decision_maker", {}).get("score", 0)
                    ]
                    overall_score = sum(scores) / len(scores)
                    
                    # Add to leads if score is promising
                    if overall_score >= 6.0:  # Threshold for good leads
                        lead = {
                            **business,
                            "analysis": analysis,
                            "validation": validation,
                            "overall_score": overall_score,
                            "category": business_type,
                            "city": city,
                            "state": state
                        }
                        self.logger.info(f"Added validated lead: {business['name']} with score {overall_score}")
                        return lead
                else:
                    self.logger.info(f"Lead rejected by DeepSeek validation: {business['name']}")
            else:
                self.logger.warning(f"No analysis returned for {business['name']}")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error processing business {business.get('name', 'Unknown')}: {str(e)}")
            return None

    def get_phone_leads(self, city: str, state: str, business_type: str) -> List[Dict]:
        """Get phone leads for a specific city and business type"""
        self.logger.info(f"Getting phone leads for {business_type} in {city}, {state}")
        
        # Check if this is a target business type
        if not any(btype[0] == business_type for btype in BUSINESS_TYPES):
            self.logger.info(f"Skipping non-target business type: {business_type}")
            return []
        
        # Search for businesses using Grok
        businesses = self._search_businesses_with_grok(city, state, business_type)
        
        leads = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.grok_api_keys)) as executor:
            future_to_business = {
                executor.submit(self._process_business_parallel, business, city, state, business_type): business
                for business in businesses
            }
            
            for future in concurrent.futures.as_completed(future_to_business):
                business = future_to_business[future]
                try:
                    lead = future.result()
                    if lead:
                        leads.append(lead)
                except Exception as e:
                    self.logger.error(f"Error processing business {business.get('name', 'Unknown')}: {str(e)}")
        
        self.logger.info(f"Found {len(leads)} qualified leads")
        return leads

    def save_to_firebase(self, leads):
        """Save leads to Firebase with city and business type organization"""
        try:
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Group leads by city and business type
            leads_by_city = {}
            for lead in leads:
                city = lead.get('city', 'Unknown')
                business_type = lead.get('category', 'Unknown')  # Use category instead of business_type
                
                if city not in leads_by_city:
                    leads_by_city[city] = {}
                if business_type not in leads_by_city[city]:
                    leads_by_city[city][business_type] = []
                
                # Ensure all required fields for frontend sorting are present
                lead_data = {
                    **lead,
                    'city': city,
                    'business_type': business_type,
                    'timestamp': timestamp,
                    'overall_score': lead.get('overall_score', 0)
                }
                
                leads_by_city[city][business_type].append(lead_data)
            
            # Save to Firebase
            for city, business_types in leads_by_city.items():
                for business_type, city_leads in business_types.items():
                    # Create a unique key for this batch
                    batch_key = f"{city}_{business_type}_{timestamp}"
                    
                    # Prepare the data structure
                    data = {
                        "metadata": {
                            "city": city,
                            "business_type": business_type,
                            "timestamp": timestamp,
                            "total_leads": len(city_leads)
                        },
                        "leads": city_leads
                    }
                    
                    # Save to Firebase using REST API
                    url = f"{self.firebase_url}/phoneLeads/{city}/{business_type}/{batch_key}.json"
                    response = requests.put(url, json=data)
                    
                    if response.status_code == 200:
                        self.logger.info(f"Saved {len(city_leads)} leads for {business_type} in {city}")
                    else:
                        self.logger.error(f"Failed to save leads: {response.status_code} - {response.text}")
                        return False
            
            self.logger.info(f"Successfully saved leads to Firebase")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving to Firebase: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Scrape phone leads for businesses')
    parser.add_argument('--num-cities', type=int, default=5, help='Number of cities to scrape')
    parser.add_argument('--num-business-types', type=int, default=3, help='Number of business types to scrape per city')
    args = parser.parse_args()

    # Initialize scraper with all available API keys
    scraper = PhoneLeadScraper([
        GROK_API_KEY,
        GROK_API_KEY_2,
        GROK_API_KEY_3,
        GROK_API_KEY_4
    ])

    # Get random cities and business types
    selected_cities = random.sample(MAJOR_CITIES, min(args.num_cities, len(MAJOR_CITIES)))
    selected_business_types = random.sample(BUSINESS_TYPES, min(args.num_business_types, len(BUSINESS_TYPES)))

    all_leads = []
    for city, state in selected_cities:
        for business_type, description in selected_business_types:
            print(f"Scraping leads for {business_type} in {city}, {state}")
            leads = scraper.get_phone_leads(city, state, business_type)
            all_leads.extend(leads)

    # Save all leads to Firebase
    if all_leads:
        scraper.save_to_firebase(all_leads)
        print(f"Successfully saved {len(all_leads)} leads to Firebase")
    else:
        print("No leads were found")

if __name__ == "__main__":
    main() 