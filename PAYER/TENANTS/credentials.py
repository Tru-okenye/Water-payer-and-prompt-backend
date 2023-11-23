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


def generate_access_token():
    # Load API keys from the environment file
    api_key = config('API_KEY')
    api_secret = config('API_SECRET')
    token_url = config('TOKEN_URL')

    # Set up the data for the token request
    data = {
        'grant_type': 'client_credentials',
    }

    # Make the request to the token URL using client credentials
    response = requests.post(
        token_url,
        auth=HTTPBasicAuth(api_key, api_secret),
        data=data
    )

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response and extract the access token
        access_token = response.json().get('access_token')
        return access_token
    else:
        # If the request was not successful, print an error message
        print(f"Error generating access token: {response.status_code} - {response.text}")
        return None



def generate_password(API_KEY, API_SECRET, reference_id):
    # Generate password
    timestamp = generate_timestamp()
    data = API_KEY + API_SECRET + timestamp + reference_id
    password = base64.b64encode(hashlib.sha256(data.encode()).digest()).decode('utf-8')

    print(f"Generated Password: {password}") 
    return password

def generate_timestamp():
    # Generate timestamp
    return datetime.now().strftime("%Y%m%d%H%M%S")


