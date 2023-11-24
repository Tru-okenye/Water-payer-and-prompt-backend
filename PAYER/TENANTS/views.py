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

@csrf_exempt
@api_view(['POST'])
def initiate_payment(request, tenant_id):
    url = settings.ENDPOINT
    tenant = get_object_or_404(Tenant, pk=tenant_id)
    phone_number = tenant.phone_number
    reference_id = f"PAYMENT_{tenant.id}"
    formatted_amount = int(tenant.amount_due * 100)  # convert to cents

    access_token = generate_access_token()
    password = generate_password()

    payload = {
        'BusinessShortCode': settings.BUSINESS_SHORT_CODE,
        'Password': password,
        'Timestamp': generate_timestamp(),
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': formatted_amount,
        'PartyA': phone_number,
        'PartyB': settings.BUSINESS_SHORT_CODE,
        'PhoneNumber': phone_number,
        'CallBackURL': 'https://water-payer-37119e2b1a5e.herokuapp.com/api/payment-callback/',  
        'AccountReference': reference_id,
        'TransactionDesc': 'Water Bill Payment'
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        print("Request Payload:", payload)
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)

        if response.status_code == 200:
            response_data = response.json()

            # Extract the information needed for STK push from the response
            merchant_request_id = response_data.get('MerchantRequestID')
            checkout_request_id = response_data.get('CheckoutRequestID')

            # Return the information to your React frontend
            return Response({
                'status': 'success',
                'message': 'Payment initiation successful',
                'merchant_request_id': merchant_request_id,
                'checkout_request_id': checkout_request_id,
            })

        else:
            # Handle other status codes or provide more specific error messages
            return Response({"status": "error", "error": f"Invalid response {response.text}"}, status=response.status_code)

    except HTTPError as e:
        # Handle HTTP errors
        response_data = {"status": "error", "error": f"HTTP error: {str(e)}"}
        return Response(response_data, status=500)

    except RequestException as e:
        # Handle other request exceptions
        response_data = {"status": "error", "error": f"Failed to initiate payment: {str(e)}"}
        return Response(response_data, status=500)
    
@csrf_exempt
@api_view(['POST'])
def payment_callback(request):
    if request.method == 'POST':
        try:
            # Extract relevant information from the callback
            data = json.loads(request.body.decode('utf-8'))
            result_code = data.get('ResultCode')
            result_desc = data.get('ResultDesc')
            merchant_request_id = data.get('MerchantRequestID')
            checkout_request_id = data.get('CheckoutRequestID')

            # Process the payment response
            if result_code == '0':
                # Payment was successful, update your database or perform any other necessary actions
                # For example, update PaymentTransaction model with the payment details
                # payment_transaction = PaymentTransaction.objects.get(merchant_request_id=merchant_request_id)
                # payment_transaction.status = 'success'
                # payment_transaction.save()

                return Response({'status': 'success', 'message': 'Payment successful'})
            else:
                # Payment failed, handle accordingly
                return Response({'status': 'error', 'message': f'Payment failed: {result_desc}'})

        except json.JSONDecodeError as e:
            return Response({'status': 'error', 'message': 'Invalid JSON data in the callback'}, status=400)

    return Response({'status': 'error', 'message': 'Invalid request method'}, status=405)