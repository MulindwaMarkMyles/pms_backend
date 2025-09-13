from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantViewSet, TenantTypeViewSet

router = DefaultRouter()
router.register(r'tenants', TenantViewSet)
router.register(r'tenant-types', TenantTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]