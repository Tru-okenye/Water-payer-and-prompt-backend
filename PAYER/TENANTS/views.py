# views.py

  
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Tenant
from .serializers import TenantSerializer
from django.http import JsonResponse
import requests
from requests.auth import HTTPBasicAuth
from django.views.decorators.csrf import csrf_exempt
import json
import logging
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
                # Add other fields you want to include
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
    amount = str(tenant.amount_due)
    reference_id = f"PAYMENT_{tenant.id}"
    formatted_amount = int(tenant.amount_due * 100)  # convert to cents
    access_token = generate_access_token(settings.API_KEY, settings.API_SECRET)

    payload = {
        'BusinessShortCode': settings.BUSINESS_SHORT_CODE,
        'Password': generate_password(settings.API_KEY, settings.API_SECRET, reference_id),
        'Timestamp': generate_timestamp(),
        'TransactionType': 'CustomerBuyGoodsOnline',
        'Amount': formatted_amount,
        'PartyA': phone_number,
        'PartyB': settings.BUSINESS_SHORT_CODE,
        'PhoneNumber': phone_number,
        'CallBackURL': settings.CALLBACK_URL,
        'AccountReference': reference_id,
        'TransactionDesc': 'Water Bill Payment'
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"API Key: {settings.API_KEY}")
            print(f"API Secret: {settings.API_SECRET}")
            print(f"Access Token: {access_token}")
            print(f"Token Response: {response.json()}")
            print(f"Amount: {formatted_amount}")
        else:
            print(f"Error response from Safaricom: {response.text}")
            return JsonResponse({"error": "Failed to obtain access token"}, status=response.status_code)

        return JsonResponse({"message": "Payment initiation successful"})
    except Exception as e:
        print(f"Error during payment initiation: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['GET'])
def check_payment_status(request, tenant_id):
    try:
        tenant = get_object_or_404(Tenant, pk=tenant_id)
        api_key = settings.API_KEY
        api_secret = settings.API_SECRET
        business_short_code = settings.BUSINESS_SHORT_CODE
        phone_number = tenant.phone_number
        reference_id = f"PAYMENT_{tenant.id}"
        endpoint = settings.QUERY

        payload = {
            "BusinessShortCode": business_short_code,
            "Password": generate_password(api_key, api_secret, reference_id),
            "Timestamp": generate_timestamp(),
            "CheckoutRequestID": reference_id,
        }

        headers = {
            "Authorization": "Bearer " + generate_access_token(api_key, api_secret),
            "Content-Type": "application/json"
        }

        response = requests.post(endpoint, json=payload, headers=headers)

        # Handle the response from Safaricom and update your database accordingly
        return JsonResponse({"message": "Payment status checked successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def payment_callback(request):
    try:
        data = request.body.decode('utf-8')
        if not data:
            return JsonResponse({"error": "Empty callback data"}, status=400)

        payload = json.loads(data)
        account_reference = payload.get('AccountReference', None)

        if account_reference:
            tenant = get_object_or_404(Tenant, tenant_id=account_reference)
            tenant.is_paid = True
            tenant.save()
            return JsonResponse({"message": "Payment callback received and processed"})
        else:
            return JsonResponse({"error": "Invalid callback data"}, status=400)

    except json.JSONDecodeError as e:
        return JsonResponse({"error": f"Error decoding JSON: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
