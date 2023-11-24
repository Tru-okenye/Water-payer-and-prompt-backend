# views.py

  
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Tenant, PaymentTransaction
from .serializers import TenantSerializer, PaymentTransactionSerializer
from django.http import JsonResponse
import requests
from requests.auth import HTTPBasicAuth
from django.views.decorators.csrf import csrf_exempt
from requests.exceptions import RequestException, HTTPError

import json

from django.shortcuts import get_object_or_404
from .credentials import generate_access_token, generate_password, generate_timestamp
from django.conf import settings

# tenants records 
class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

  
@csrf_exempt
def verify_login(request):
    if request.method == 'POST':
        try:
            # Use request.body to get the raw JSON data
            data = json.loads(request.body.decode('utf-8'))

            # Extract the values from the JSON data
            name = data.get('name')
            tenant_id = data.get('tenant_id')

            print(f"Received data - Name: {name}, Tenant ID: {tenant_id}")

            # Check if the tenant exists
            try:
                tenant = get_object_or_404(Tenant, name=name, tenant_id=tenant_id)
                return JsonResponse({'success': True, 'message': 'Login successful'})
            except:
                return JsonResponse({'success': False, 'message': 'Invalid login credentials'})

        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data in the request'}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def authenticated_tenant_details(request, tenant_id):
    if request.method == 'GET':
        try:
            tenant = Tenant.objects.get(tenant_id=tenant_id)

            data = {
                'id': tenant.id,
                'name': tenant.name,
                'phone_number': tenant.phone_number,
                'amount_due': tenant.amount_due,
               
            }

            return JsonResponse(data)
        except Tenant.DoesNotExist:
            return JsonResponse({'error': 'Tenant details not found'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


# payment handling 


def initiate_payment(request, tenant_id):
    url = settings.ENDPOINT
    tenant = get_object_or_404(Tenant, pk=tenant_id)
    phone_number = tenant.phone_number
    reference_id = f"PAYMENT_{tenant.id}"
    formatted_amount = int(tenant.amount_due * 100)  # convert to cents
    print("Before generate_access_token")
    access_token = generate_access_token()
    print("After generate_access_token")
    password = generate_password()

    request = {
        'BusinessShortCode': settings.BUSINESS_SHORT_CODE,
        'Password': password,
        'Timestamp': generate_timestamp(),
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': formatted_amount,
        'PartyA': phone_number,
        'PartyB': settings.BUSINESS_SHORT_CODE,
        'PhoneNumber': phone_number,
        'CallBackURL': 'https://water-payer-37119e2b1a5e.herokuapp.com/api/check-payment-status/',
        'AccountReference': reference_id,
        'TransactionDesc': 'Water Bill Payment'
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
    }
    
    try:
        response = requests.post(url, json=request, headers=headers)
        print("Request Payload:", request)
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)

        if response.status_code == 200:
            print(f"API Key: {settings.API_KEY}")
            print(f"API Secret: {settings.API_SECRET}")
            print(f"Access Token: {access_token}")
            print(f"Token Response: {response.json()}")
            print(f"Amount: {formatted_amount}")

            stk_data = response.json()
            response_code = stk_data.get('ResponseCode')
            payment_transaction = PaymentTransaction.objects.create(
                tenant_id=tenant.id,
                checkout_request_id=stk_data.get('CheckoutRequestID'),
               
            )
            
            print(f"Checkout Request ID: {stk_data.get('CheckoutRequestID')}")

            if response_code == '0':
                # STK push was successful, respond with success and the CheckoutRequestID
                response_data = {
                     "status": "success",
                     "checkoutRequestID": stk_data['CheckoutRequestID'],
                     "payment_transaction_id": payment_transaction.id, 
                     "created_at": payment_transaction.created_at
                }
                return JsonResponse(response_data)
            
            else:
                # STK push failed, respond with error message and the ResponseDescription
                return JsonResponse({"status": "error", "error": stk_data['ResponseDescription']})
        elif response.status_code == 400 or response.status_code == 500:
            stk_data = response.json()
            return JsonResponse({"status": "error", "error": stk_data})
        else:
            return JsonResponse({"status": "error", "error": f"Invalid response {response.text} received."})

    except requests.exceptions.RequestException as e:
        # Handle any exceptions or errors here
        response_data = {"status": "error", "error": f"Failed to initiate payment: {str(e)}"}
        return JsonResponse(response_data, status=500)
    
@csrf_exempt    
def check_payment_status(request, checkout_request_id):
    try:
        url = settings.QUERY
        timestamp = generate_timestamp()
        business_short_code = settings.MPESA_SHORTCODE
        password = generate_password()

        payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + generate_access_token() 
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses

        # Handle the response from Safaricom
        data = response.json()
        result_code = data.get("ResultCode")

        if result_code == 0:  # Success
            tenant_id = int(checkout_request_id.split("_")[1])
            tenant = Tenant.objects.get(id=tenant_id)
            tenant.is_paid = True
            tenant.save()
            return JsonResponse({"status": "success", "data": data})
        else:
            return JsonResponse({"status": "error", "data": data})

    except HTTPError as e:
        # Handle HTTP errors
        response_data = {"status": "error", "data": f"HTTP error: {str(e)}"}
        return JsonResponse(response_data, status=response.status_code)
    except RequestException as e:
        # Handle other request exceptions
        response_data = {"status": "error", "data": f"Request error: {str(e)}"}
        return JsonResponse(response_data, status=500)
    
@api_view(['GET'])
def get_payment_transactions(request):
    # Retrieve all payment transactions from the database
    transactions = PaymentTransaction.objects.all()

    # Serialize the queryset using the serializer
    serializer = PaymentTransactionSerializer(transactions, many=True)

    # Return the serialized data as JSON response
    return Response(serializer.data)

