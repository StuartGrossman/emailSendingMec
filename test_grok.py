#!/usr/bin/env python3
import requests
import json
import sys
import os
from datetime import datetime

def save_to_file(data, filename="response_log.json"):
    """Save data to a local file"""
    try:
        # Create a logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        # Create a timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"logs/{timestamp}_{filename}"
        
        # Write data to file
        with open(filepath, 'w') as f:
            if isinstance(data, dict) or isinstance(data, list):
                json.dump(data, f, indent=2)
            else:
                f.write(str(data))
        
        print(f"Data saved to file: {filepath}")
        return filepath
    except Exception as e:
        print(f"Failed to save data to file: {str(e)}")
        return None

def test_grok_api():
    """Test the Grok API directly"""
    print("Testing Grok API...")
    
    # Prepare the request to Grok API
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer xai-S375bT9UgdT3qzjhXHO88F3WHbmGgZzlzJMbw05d9Bkv3s6cGwZcM3fff40fb7j8gi9xgLpmnrgSurmE"
    }
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a test assistant."
            },
            {
                "role": "user",
                "content": "Testing. Just say hi and hello world and nothing else."
            }
        ],
        "model": "grok-2-latest",
        "stream": False,
        "temperature": 0
    }
    
    # Save request details
    print("Request URL: https://api.x.ai/v1/chat/completions")
    print(f"Request headers: {json.dumps(headers, indent=2)}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    save_to_file(payload, "direct_grok_request.json")
    
    try:
        # Make the request to Grok API
        print("Sending request to Grok API...")
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Log response details
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
        response_text = response.text
        print(f"Response text length: {len(response_text)} characters")
        print(f"Response text preview: {response_text[:200]}...")
        
        # Save response to file
        save_to_file(response_text, "direct_grok_response.txt")
        
        # Try to parse as JSON
        try:
            response_json = response.json()
            print("Response parsed as JSON successfully")
            save_to_file(response_json, "direct_grok_response.json")
            
            # Extract and print content
            content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "No content")
            print(f"Content: {content}")
            
            return True, response_json
        except json.JSONDecodeError as e:
            print(f"Failed to parse response as JSON: {str(e)}")
            return False, response_text
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return False, str(e)

if __name__ == "__main__":
    print("Direct Grok API Test")
    print("=" * 50)
    success, result = test_grok_api()
    print("=" * 50)
    print(f"Test {'succeeded' if success else 'failed'}")
    print("=" * 50) 