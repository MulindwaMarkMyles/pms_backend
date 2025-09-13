from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EstateViewSet, 
    BlockViewSet, 
    ApartmentViewSet, 
    AmenityViewSet, 
    FurnishingViewSet,
    OwnerDashboardViewSet
)

router = DefaultRouter()
router.register(r'estates', EstateViewSet)
router.register(r'blocks', BlockViewSet)
router.register(r'apartments', ApartmentViewSet)
router.register(r'amenities', AmenityViewSet)
router.register(r'furnishings', FurnishingViewSet)
router.register(r'owner', OwnerDashboardViewSet, basename='owner')

urlpatterns = [
    path('', include(router.urls)),
]