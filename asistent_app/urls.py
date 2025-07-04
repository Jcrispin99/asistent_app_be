"""
URL configuration for asistent_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.auth_serializers import CustomTokenObtainPairSerializer

# Vista personalizada para login con email o username
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/companies/', include('companies.urls')),
    path('api/v1/departments/', include('departments.urls')),
    path('api/v1/positions/', include('positions.urls')),
    path('api/v1/employees/', include('employees.urls')),
    path('api/v1/holidays/', include('holidays.urls')),
    path('api/v1/attendance/', include('attendance.urls')),
    path('api/v1/users/', include('users.urls')),

    # Autenticación JWT
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Login/Logout para la API browsable
    path('api-auth/', include('rest_framework.urls')),
    # Documentación de la API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
