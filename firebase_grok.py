#!/usr/bin/env python3
import requests
import json
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

def get_grok_response(query="Testing. Just say hi and hello world and nothing else."):
    """Get a response from the Grok API"""
    print(f"Getting response from Grok API for query: {query}")
    
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
                "content": query
            }
        ],
        "model": "grok-2-latest",
        "stream": False,
        "temperature": 0
    }
    
    # Make the request to Grok API
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check response status
        if response.status_code != 200:
            print(f"Grok API returned non-200 status code: {response.status_code}")
            print(f"Response text: {response.text}")
            return None
        
        # Parse response JSON
        try:
            response_json = response.json()
            # Extract the content
            content = response_json.get("choices", [{}])[0].get("message", {}).get("content", "No content")
            print(f"Received response from Grok: {content}")
            return response_json
        except json.JSONDecodeError as e:
            print(f"Failed to parse response as JSON: {str(e)}")
            return None
            
    except Exception as e:
        print(f"Error making request to Grok API: {str(e)}")
        return None

def send_to_firebase(grok_data):
    """Send data to Firebase Realtime Database"""
    print("Sending data to Firebase...")
    
    # Firebase configuration
    firebase_url = "https://emailsender-44bcc-default-rtdb.firebaseio.com/grok_responses.json"
    
    # Prepare data for Firebase
    firebase_data = {
        'query': grok_data.get("choices", [{}])[0].get("message", {}).get("content", "No content"),
        'response': grok_data,
        'timestamp': datetime.now().isoformat()
    }
    
    # Save request to file
    save_to_file(firebase_data, "firebase_request.json")
    
    try:
        # Send data to Firebase
        firebase_response = requests.post(firebase_url, json=firebase_data)
        
        # Check response status
        if firebase_response.status_code != 200:
            print(f"Firebase returned non-200 status code: {firebase_response.status_code}")
            print(f"Response text: {firebase_response.text}")
            return False
        
        # Save response to file
        save_to_file(firebase_response.json(), "firebase_response.json")
        
        print("Data successfully sent to Firebase")
        print(f"Firebase response: {firebase_response.json()}")
        return True
        
    except Exception as e:
        print(f"Error sending data to Firebase: {str(e)}")
        return False

def main():
    print("Grok to Firebase Integration")
    print("=" * 50)
    
    # Get response from Grok
    grok_response = get_grok_response("Tell me a joke about programming")
    
    if grok_response:
        print("=" * 50)
        print("Got response from Grok")
        
        # Send to Firebase
        success = send_to_firebase(grok_response)
        
        print("=" * 50)
        print(f"Firebase upload {'succeeded' if success else 'failed'}")
    else:
        print("Failed to get response from Grok")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 