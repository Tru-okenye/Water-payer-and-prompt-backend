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
class MpesaAccessToken:
    t = requests.get(TOKEN_URL,
                     auth=HTTPBasicAuth(API_KEY,  API_SECRET))
    access_token = json.loads(t.text)
    validated_access_token = access_token["access_token"]
# def generate_access_token():
#     # Make the request to the token URL using client credentials
#     auth = HTTPBasicAuth(API_KEY, API_SECRET)
    

#     try:
#         response = requests.post(
#             TOKEN_URL,
#             auth=auth,
           
#         )
#         response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)

#         access_token = response.json().get("access_token")
#         print("Token URL Response:", response.text)
#         return access_token

#     except requests.exceptions.RequestException as e:
#         # Log the error for debugging
#         print(f"Error during token generation: {str(e)}")
#         return None

#     except ValueError as e:
#         # Log the error for debugging
#         print(f"Error decoding JSON during token generation: {str(e)}")
#         return None



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


