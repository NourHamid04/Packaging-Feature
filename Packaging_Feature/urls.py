from django.contrib import admin
from django.urls import path
from inventory.api import api
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.authtoken.views import obtain_auth_token





urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),  # For token-based auth if needed
]
