



from django.urls import path, include
from rest_framework.routers import DefaultRouter
from TENANTS.views import TenantViewSet, initiate_payment, verify_login, authenticated_tenant_details, payment_callback

# Create a router and register the TenantViewSet with it.
router = DefaultRouter()
router.register(r'tenants', TenantViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/verify-login/', verify_login, name='verify-login'),
    path('api/tenant-details/<int:tenant_id>/', authenticated_tenant_details, name='tenant-details'),
    path('api/initiate-payment/<int:tenant_id>/', initiate_payment, name='initiate-payment'),
    path('api/payment-callback/', payment_callback, name='payment-callback'),
]