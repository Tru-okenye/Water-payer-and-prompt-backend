"""PAYER URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from TENANTS.views import TenantViewSet, initiate_payment, check_payment_status, payment_callback, verify_login, authenticated_tenant_details


router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/verify-login/', verify_login, name='verify_login'),
    path('api/authenticated-tenant-details/<int:tenant_id>/', authenticated_tenant_details, name='authenticated-tenant-details'),
    path('api/tenants/<int:tenant_id>/initiate-payment/', initiate_payment, name='initiate-payment'),
    path('api/tenants/<int:tenant_id>/check-payment-status/', check_payment_status, name='check-payment-status'),
    path('api/payment-callback/', payment_callback, name='payment-callback'),
   


    
]