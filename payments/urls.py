from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentStatusViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)
router.register(r'payment-statuses', PaymentStatusViewSet)

urlpatterns = [
    path('', include(router.urls)),
]