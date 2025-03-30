#!/usr/bin/env python3
import pytest
from src.services.phone_lead_scraper import PhoneLeadScraper
from src.config.config import GROK_API_KEYS
from unittest.mock import patch, MagicMock
import json

def test_phone_lead_scraper_initialization():
    """Test that PhoneLeadScraper initializes correctly."""
    scraper = PhoneLeadScraper(GROK_API_KEYS[0])
    assert scraper.api_key is not None
    assert scraper.headers is not None
    assert scraper.logger is not None

def test_grok_connection():
    """Test connection to Grok API."""
    scraper = PhoneLeadScraper(GROK_API_KEYS[0])
    assert scraper.test_grok_connection() is True

def test_get_phone_leads():
    """Test getting phone leads for a business type."""
    scraper = PhoneLeadScraper(GROK_API_KEYS[0])
    leads = scraper.get_phone_leads("San Francisco", "CA", "Software Companies")
    assert isinstance(leads, list)

def test_save_leads_to_firebase():
    """Test saving leads to Firebase."""
    scraper = PhoneLeadScraper(GROK_API_KEYS[0])
    test_leads = [
        {
            "name": "Test Company",
            "phone": "123-456-7890",
            "address": "123 Test St",
            "city": "San Francisco",
            "state": "CA"
        }
    ]
    success = scraper.save_leads_to_firebase(test_leads, "San Francisco", "CA", "Software Companies")
    assert success is True

@pytest.fixture
def mock_grok_response():
    return {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "tech_stack": {
                        "score": 7,
                        "current_systems": ["Basic POS", "Paper records"],
                        "limitations": ["No integration", "Manual data entry"],
                        "integration_challenges": ["Multiple systems", "Legacy software"]
                    },
                    "operations": {
                        "score": 8,
                        "scale": "Small to medium",
                        "efficiency": "Low",
                        "manual_processes": ["Inventory tracking", "Customer communication"]
                    },
                    "growth_potential": {
                        "score": 9,
                        "market_position": "Strong local presence",
                        "growth_indicators": ["Expanding customer base", "New service offerings"],
                        "tech_readiness": "High"
                    },
                    "software_opportunity": {
                        "score": 8,
                        "pain_points": ["Manual scheduling", "Inventory management"],
                        "roi_areas": ["Reduced manual work", "Better customer service"],
                        "integration_needs": ["POS system", "Customer database"]
                    },
                    "decision_maker": {
                        "score": 7,
                        "stakeholders": ["Owner", "Manager"],
                        "investment_signals": ["Recent website update", "Growing team"],
                        "contact_approach": "Direct owner contact"
                    },
                    "sales_conversation": {
                        "opening_points": ["Current scheduling system", "Customer management"],
                        "pain_points": ["Manual processes", "Time management"],
                        "roi_examples": ["30% time savings", "Improved customer satisfaction"],
                        "solutions": ["Automated scheduling", "Integrated CRM"],
                        "questions": ["Current tech challenges?", "Growth plans?"]
                    }
                })
            }
        }]
    }

@pytest.fixture
def mock_business():
    return {
        "name": "Test Auto Repair",
        "phone": "555-0123",
        "address": "123 Main St, San Francisco, CA",
        "website": "www.testauto.com",
        "description": "Family-owned auto repair shop using basic scheduling software and paper-based inventory management.",
        "employees": "5-10",
        "years_in_business": 15
    }

@pytest.fixture
def scraper():
    return PhoneLeadScraper("test_api_key")

def test_phone_lead_scraper_initialization(scraper):
    """Test that the scraper initializes correctly with an API key."""
    assert scraper.api_key == "test_api_key"
    assert "Content-Type" in scraper.headers
    assert "Authorization" in scraper.headers
    assert scraper.business_categories is not None

def test_business_categories_initialization(scraper):
    """Test that business categories are properly initialized."""
    categories = scraper.business_categories
    assert "auto_repair" in categories
    assert "medical" in categories
    assert "retail" in categories
    
    # Check category structure
    for category in categories.values():
        assert "keywords" in category
        assert "tech_indicators" in category
        assert "pain_points" in category

@patch('requests.post')
def test_analyze_business_with_grok(mock_post, scraper, mock_business, mock_grok_response):
    """Test the business analysis functionality using Grok."""
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: mock_grok_response
    )
    
    category_info = scraper.business_categories["auto_repair"]
    analysis = scraper._analyze_business_with_grok(mock_business, category_info)
    
    assert analysis is not None
    assert "tech_stack" in analysis
    assert "operations" in analysis
    assert "growth_potential" in analysis
    assert "software_opportunity" in analysis
    assert "decision_maker" in analysis
    assert "sales_conversation" in analysis
    
    # Check scores
    assert analysis["tech_stack"]["score"] == 7
    assert analysis["operations"]["score"] == 8
    assert analysis["growth_potential"]["score"] == 9
    assert analysis["software_opportunity"]["score"] == 8
    assert analysis["decision_maker"]["score"] == 7

@patch('requests.post')
def test_get_phone_leads(mock_post, scraper, mock_grok_response):
    """Test the phone lead retrieval functionality."""
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: mock_grok_response
    )
    
    leads = scraper.get_phone_leads("San Francisco", "CA", "auto_repair")
    
    assert isinstance(leads, list)
    if leads:  # If any leads were found
        lead = leads[0]
        assert "name" in lead
        assert "phone" in lead
        assert "analysis" in lead
        assert "overall_score" in lead
        assert "category" in lead
        assert lead["overall_score"] >= 6.0  # Check minimum score threshold

@patch('requests.patch')
def test_save_leads_to_firebase(mock_patch, scraper):
    """Test saving leads to Firebase."""
    mock_patch.return_value = MagicMock(status_code=200)
    
    leads = [{
        "name": "Test Business",
        "phone": "555-0123",
        "analysis": {"score": 8},
        "overall_score": 8.0,
        "category": "auto_repair"
    }]
    
    success = scraper.save_leads_to_firebase(
        leads=leads,
        city="San Francisco",
        state="CA",
        business_type="auto_repair"
    )
    
    assert success is True
    mock_patch.assert_called_once()

def test_business_category_matching(scraper):
    """Test that businesses are correctly matched to categories."""
    test_cases = [
        {
            "description": "Auto repair shop with modern equipment",
            "expected_category": "auto_repair"
        },
        {
            "description": "Family dental practice in downtown",
            "expected_category": "medical"
        },
        {
            "description": "Local gym with personal trainers",
            "expected_category": "fitness"
        }
    ]
    
    for case in test_cases:
        business = {"description": case["description"]}
        category = None
        
        for cat_name, cat_info in scraper.business_categories.items():
            if any(kw.lower() in case["description"].lower() for kw in cat_info["keywords"]):
                category = cat_name
                break
        
        assert category == case["expected_category"]

@patch('requests.post')
def test_grok_error_handling(mock_post, scraper, mock_business):
    """Test error handling in Grok analysis."""
    mock_post.return_value = MagicMock(
        status_code=500,
        text="API Error"
    )
    
    category_info = scraper.business_categories["auto_repair"]
    analysis = scraper._analyze_business_with_grok(mock_business, category_info)
    
    assert analysis == {}

@patch('requests.patch')
def test_firebase_error_handling(mock_patch, scraper):
    """Test error handling when saving to Firebase."""
    mock_patch.return_value = MagicMock(
        status_code=500,
        text="Firebase Error"
    )
    
    leads = [{"name": "Test Business"}]
    success = scraper.save_leads_to_firebase(
        leads=leads,
        city="San Francisco",
        state="CA",
        business_type="auto_repair"
    )
    
    assert success is False

if __name__ == "__main__":
    pytest.main([__file__, '-v']) 