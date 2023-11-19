import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
import hashlib
import logging

from decouple import config  

logger = logging.getLogger(__name__)

# Load values from environment variables
API_KEY = config('API_KEY')
API_SECRET = config('API_SECRET')
TOKEN_URL = config('TOKEN_URL')
# ... (other variables)

def generate_access_token():
    auth = HTTPBasicAuth(API_KEY, API_SECRET)
    token_url = TOKEN_URL
    
    try:
        response = requests.get(token_url, auth=auth)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)

        access_token = response.json().get("access_token")
        return access_token

    except requests.exceptions.RequestException as e:
        # Log the error for debugging
        logger.error(f"Error during token generation: {str(e)}")
        raise  # Re-raise the exception to be handled at a higher level

    except json.JSONDecodeError as e:
        # Log the error for debugging
        logger.error(f"Error decoding JSON during token generation: {str(e)}")
        raise  # Re-raise the exception to be handled at a higher level

def generate_password(reference_id):
    # Generate password
    timestamp = generate_timestamp()
    data = API_KEY + API_SECRET + timestamp + reference_id
    password = base64.b64encode(hashlib.sha256(data.encode()).digest()).decode('utf-8')

    print(f"Generated Password: {password}") 
    return password

def generate_timestamp():
    # Generate timestamp
    return datetime.now().strftime("%Y%m%d%H%M%S")

# ... (other functions)
