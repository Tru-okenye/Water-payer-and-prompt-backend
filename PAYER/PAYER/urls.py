

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from TENANTS.views import TenantViewSet, initiate_payment, check_payment_status, verify_login, authenticated_tenant_details


router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/verify-login/', verify_login, name='verify_login'),
    path('api/authenticated-tenant-details/<int:tenant_id>/', authenticated_tenant_details, name='authenticated-tenant-details'),
    path('api/tenants/<int:tenant_id>/initiate-payment/', initiate_payment, name='initiate-payment'),
    path('api/tenants/<int:tenant_id>/check-payment-status/', check_payment_status, name='check-payment-status'),
    
]