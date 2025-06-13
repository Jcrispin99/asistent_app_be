# Solución al Problema de Autenticación

## Problema Identificado

El frontend está usando endpoints inconsistentes para la autenticación:
- `/api-auth/login/` - Endpoint del Django REST Framework browsable API (para navegador)
- `/api/v1/users/users/` - Endpoint personalizado para obtener usuario
- `/api/auth/refresh/` - Endpoint para refresh token

Esta inconsistencia causa el error "Login error response: null" porque:
1. `/api-auth/login/` está diseñado para autenticación de sesión del navegador, no para JWT
2. Los endpoints no siguen una estructura coherente
3. El backend probablemente no está configurado correctamente para JWT

## Solución Recomendada

### 1. Configuración del Backend (Django)

El backend debe usar `djangorestframework-simplejwt` con esta configuración:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
```

```python
# urls.py
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.contrib.auth.models import User
from rest_framework import generics, serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

urlpatterns = [
    # Endpoints JWT consistentes
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/auth/user/', UserProfileView.as_view(), name='user_profile'),
    # ...
]
```

### 2. Actualización del Frontend

Actualizar `auth.api.ts` para usar endpoints consistentes:

```typescript
// Todos los endpoints bajo /api/auth/
export async function login(usernameOrEmail: string, password: string): Promise<LoginResponse> {
    const isEmail = usernameOrEmail.includes('@');
    const requestBody = isEmail 
        ? { email: usernameOrEmail, password }
        : { username: usernameOrEmail, password };
    
    const res = await fetch(`${API_BASE}/api/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
    });
    
    if (!res.ok) {
        const errBody = await res.text();
        console.error('❌ Login error response:', errBody);
        throw new Error(`Login failed: ${res.status}`);
    }
    
    const data = await res.json();
    
    // djangorestframework-simplejwt devuelve { access, refresh }
    const loginResponse: LoginResponse = {
        access: data.access,
        refresh: data.refresh,
        user: data.user || await getCurrentUser(data.access) // Obtener usuario por separado si es necesario
    };
    
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    
    return loginResponse;
}

export async function getCurrentUser(): Promise<UserProfile> {
    const token = getToken();
    if (!token) throw new Error('No token available');
    
    const res = await fetch(`${API_BASE}/api/auth/user/`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });
    
    if (!res.ok) throw new Error('Failed to get user');
    return res.json();
}

export async function refreshToken(): Promise<string> {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) throw new Error('No refresh token');
    
    const res = await fetch(`${API_BASE}/api/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
    });
    
    if (!res.ok) throw new Error('Token refresh failed');
    
    const data = await res.json();
    localStorage.setItem('access_token', data.access);
    return data.access;
}
```

### 3. Actualización de Vite Proxy

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
```

## Endpoints Finales Consistentes

- `POST /api/auth/login/` - Login (devuelve access + refresh tokens)
- `POST /api/auth/refresh/` - Refresh token
- `GET /api/auth/user/` - Obtener perfil del usuario actual
- `POST /api/auth/verify/` - Verificar token

## Beneficios de esta Solución

1. **Consistencia**: Todos los endpoints de auth bajo `/api/auth/`
2. **Estándar**: Usa djangorestframework-simplejwt que es el estándar de la industria
3. **Seguridad**: JWT con refresh tokens y blacklisting
4. **Simplicidad**: Un solo proxy en Vite para `/api`
5. **Mantenibilidad**: Estructura clara y predecible

Esta configuración debería resolver completamente el problema de "Login error response: null".