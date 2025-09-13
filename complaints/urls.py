from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComplaintViewSet, ComplaintStatusViewSet, ComplaintCategoryViewSet

router = DefaultRouter()
router.register(r'complaints', ComplaintViewSet)
router.register(r'complaint-statuses', ComplaintStatusViewSet)
router.register(r'complaint-categories', ComplaintCategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]