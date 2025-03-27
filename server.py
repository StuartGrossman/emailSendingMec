from flask import Flask, jsonify, request
import requests
import json
import logging
import sys
import traceback
import os
from datetime import datetime

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

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
        
        logger.info(f"Data saved to file: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save data to file: {str(e)}")
        return None

@app.route('/')
def home():
    return jsonify({"message": "Grok API Server is running"})

@app.route('/test', methods=['GET'])
def test():
    """Simple test endpoint"""
    logger.info("Test endpoint called")
    return jsonify({"status": "ok", "message": "Server is working"})

@app.route('/save', methods=['POST'])
def save_data():
    """Endpoint to save data to a local file"""
    try:
        data = request.get_json()
        filepath = save_to_file(data, "saved_data.json")
        
        if filepath:
            return jsonify({"status": "success", "message": f"Data saved to {filepath}"})
        else:
            return jsonify({"status": "error", "message": "Failed to save data"}), 500
    except Exception as e:
        logger.error(f"Error in /save endpoint: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/grok', methods=['POST'])
def grok_query():
    try:
        # Log the raw request
        logger.info("Received request to /grok endpoint")
        logger.info(f"Request headers: {dict(request.headers)}")
        request_data_raw = request.get_data(as_text=True)
        logger.info(f"Request data: {request_data_raw}")
        
        # Save the raw request to file
        save_to_file(request_data_raw, "grok_request_raw.txt")
        
        # Parse the request JSON
        try:
            request_data = request.get_json()
            logger.info(f"Parsed request data: {request_data}")
        except Exception as e:
            logger.error(f"Failed to parse request JSON: {str(e)}")
            return jsonify({"error": "Invalid JSON in request"}), 400
        
        # Get the query from the request
        query = request_data.get('query', 'Testing. Just say hi and hello world and nothing else.')
        logger.info(f"Extracted query: {query}")
        
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
        
        # Save the request payload to file
        save_to_file(payload, "grok_request_payload.json")
        
        # Make the request to Grok API
        logger.info("Making request to Grok API...")
        logger.info(f"Request URL: https://api.x.ai/v1/chat/completions")
        logger.info(f"Request headers: {json.dumps(headers, indent=2)}")
        logger.info(f"Request payload: {json.dumps(payload, indent=2)}")
        
        try:
            grok_response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30  # Add timeout
            )
            logger.info(f"Grok API response status code: {grok_response.status_code}")
            logger.info(f"Grok API response headers: {json.dumps(dict(grok_response.headers), indent=2)}")
            response_text = grok_response.text
            logger.info(f"Grok API response text: {response_text}")
            
            # Save the raw response to file
            save_to_file(response_text, "grok_response_raw.txt")
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to make request to Grok API: {str(e)}"
            logger.error(error_msg)
            save_to_file(error_msg, "grok_error.txt")
            return jsonify({"error": error_msg}), 500
        
        # Check response status code
        if grok_response.status_code != 200:
            error_msg = f"Grok API returned non-200 status code: {grok_response.status_code}"
            logger.error(error_msg)
            save_to_file({
                "status_code": grok_response.status_code,
                "response_text": response_text
            }, "grok_error_response.json")
            return jsonify({
                "error": "Grok API request failed",
                "status_code": grok_response.status_code,
                "response": response_text
            }), 500
        
        # Parse response JSON
        try:
            grok_data = grok_response.json()
            logger.info(f"Parsed Grok API response: {json.dumps(grok_data, indent=2)}")
            
            # Save the parsed response to file
            save_to_file(grok_data, "grok_response.json")
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse Grok API response as JSON: {str(e)}"
            logger.error(error_msg)
            save_to_file({
                "error": error_msg,
                "response_text": response_text
            }, "grok_json_error.json")
            return jsonify({
                "error": "Invalid JSON response from Grok API",
                "response": response_text
            }), 500
        
        # Create a simple response with just the content
        simple_response = {
            "message": "Grok API request successful",
            "content": grok_data.get("choices", [{}])[0].get("message", {}).get("content", "No content")
        }
        
        # Return successful response
        return jsonify(simple_response)
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        logger.error("Unexpected error occurred:")
        logger.error(traceback.format_exc())
        save_to_file(error_msg, "grok_unexpected_error.txt")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting server...")
    app.run(debug=True, port=5000) 