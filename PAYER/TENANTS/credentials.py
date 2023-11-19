import requests
import json
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
import hashlib
import logging


class Credentials:
    api_key = 'lfPeIPhZ7KDHfyNCFILttArLsKhZv0Ma'
    api_secret= 'Voqvlbj5qApy6YEK'
    pass_key= 'fef66eba0f3f6485df404ac4980e3f49924cc8a8b3e6ef7dd6bbc238cdd0629c' 
    endpoint = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    business_short_code = '6437127'



# CALLBACK_URL: 'https://lets-ride-fe42d9bf40d4.herokuapp.com/api/stkquery'
# generate token
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