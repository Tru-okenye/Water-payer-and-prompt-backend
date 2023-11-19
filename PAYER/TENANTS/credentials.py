import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
import hashlib
import logging
from django.conf import settings


logger = logging.getLogger(__name__)
def generate_access_token(api_key, api_secret):
    auth = HTTPBasicAuth(api_key, api_secret)
    token_url = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    
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




def generate_password(api_key, api_secret, reference_id):
    # Generate  password


    timestamp = generate_timestamp()
    data = api_key + api_secret + timestamp + reference_id
    password = base64.b64encode(hashlib.sha256(data.encode()).digest()).decode('utf-8')

    print(f"Generated Password: {password}") 
    return password

def generate_timestamp():
    # Generate  timestamp
    return datetime.now().strftime("%Y%m%d%H%M%S")