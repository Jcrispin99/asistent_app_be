# CONFIGURACIÓN DEL BACKEND DJANGO PARA JWT
# Este archivo contiene la configuración necesaria para el backend Django
# para que funcione correctamente con el frontend actualizado

# ============================================================================
# 1. INSTALACIÓN DE DEPENDENCIAS
# ============================================================================
# pip install djangorestframework
# pip install djangorestframework-simplejwt

# ============================================================================
# 2. SETTINGS.PY
# ============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Django REST Framework
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    
    # CORS (si es necesario)
    'corsheaders',
    
    # Tus apps aquí
    # 'tu_app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Si usas CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuración de Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Configuración de JWT
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS (si el frontend está en un puerto diferente)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:5174",  # Vite dev server alternativo
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

CORS_ALLOW_CREDENTIALS = True

# ============================================================================
# 3. SERIALIZERS.PY
# ============================================================================

from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer personalizado que incluye información del usuario en la respuesta"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar información del usuario a la respuesta
        user_serializer = UserSerializer(self.user)
        data['user'] = user_serializer.data
        
        return data

# ============================================================================
# 4. VIEWS.PY
# ============================================================================

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User

class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista personalizada para login que incluye información del usuario"""
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Vista para obtener y actualizar el perfil del usuario actual"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

# ============================================================================
# 5. URLS.PY (PRINCIPAL)
# ============================================================================

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import CustomTokenObtainPairView, UserProfileView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Endpoints de autenticación JWT
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/auth/user/', UserProfileView.as_view(), name='user_profile'),
    
    # Otras rutas de tu aplicación
    # path('api/v1/', include('tu_app.urls')),
]

# ============================================================================
# 6. COMANDOS PARA CONFIGURAR
# ============================================================================

# 1. Instalar dependencias:
# pip install djangorestframework djangorestframework-simplejwt django-cors-headers

# 2. Hacer migraciones:
# python manage.py makemigrations
# python manage.py migrate

# 3. Crear superusuario (si no existe):
# python manage.py createsuperuser

# 4. Ejecutar servidor:
# python manage.py runserver

# ============================================================================
# 7. TESTING DE ENDPOINTS
# ============================================================================

# Puedes probar los endpoints con curl:

# Login:
# curl -X POST http://localhost:8000/api/auth/login/ \
#      -H "Content-Type: application/json" \
#      -d '{"username": "admin", "password": "admin"}'

# Respuesta esperada:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "user": {
#     "id": 1,
#     "username": "admin",
#     "email": "admin@example.com",
#     "first_name": "",
#     "last_name": "",
#     "is_active": true,
#     "date_joined": "2024-01-01T00:00:00Z"
#   }
# }

# Obtener usuario actual:
# curl -X GET http://localhost:8000/api/auth/user/ \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Refresh token:
# curl -X POST http://localhost:8000/api/auth/refresh/ \
#      -H "Content-Type: application/json" \
#      -d '{"refresh": "YOUR_REFRESH_TOKEN"}'