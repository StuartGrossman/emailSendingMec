#!/usr/bin/env python3
import os
import time
import json
from datetime import datetime
from src.scrapers.business_scraper_parallel import BusinessScraper, MAJOR_CITIES, BUSINESS_TYPES
from src.config.config import GROK_API_KEYS

def run_test_scraper():
    # Create testData directory if it doesn't exist
    if not os.path.exists('testData'):
        os.makedirs('testData')
    
    # Initialize scraper with first API key
    scraper = BusinessScraper(GROK_API_KEYS[0], 1)
    
    # Set start time
    start_time = time.time()
    test_duration = 30  # 30 seconds
    
    # List to store scraped businesses
    scraped_businesses = []
    
    print("Starting test scraper for 30 seconds...")
    
    try:
        # Process first city and business type only for testing
        city, state = MAJOR_CITIES[0]
        business_type, software_probability, description = BUSINESS_TYPES[0]
        
        # Get businesses from Grok
        businesses = scraper.get_businesses_from_grok(
            city, state, business_type, description,
            software_probability, [], None
        )
        
        # Process each business
        for business in businesses:
            # Check if we've exceeded the time limit
            if time.time() - start_time > test_duration:
                break
                
            # Clean and validate business data
            cleaned_business = scraper.clean_business_data(business)
            
            # Add metadata
            cleaned_business.update({
                'city': city,
                'state': state,
                'business_type': business_type,
                'scrape_timestamp': datetime.now().isoformat()
            })
            
            scraped_businesses.append(cleaned_business)
            
            # Add small delay between processing
            time.sleep(1)
    
    except Exception as e:
        print(f"Error during test scraping: {str(e)}")
    
    # Save scraped data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'testData/scraped_businesses_{timestamp}.json'
    
    with open(output_file, 'w') as f:
        json.dump(scraped_businesses, f, indent=2)
    
    print(f"\nTest completed!")
    print(f"Scraped {len(scraped_businesses)} businesses")
    print(f"Data saved to: {output_file}")
    
    return output_file

if __name__ == "__main__":
    run_test_scraper() 