from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.auth_views import register_user, get_user_profile

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', register_user, name='register_user'),
    path('api/profile/', get_user_profile, name='get_user_profile'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/core/', include('core.urls')),
    path('api/tenants/', include('tenants.urls')),
    path('api/complaints/', include('complaints.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/owners/', include('owners.urls')),
    path('api/notifications/', include('notifications.urls')),
]