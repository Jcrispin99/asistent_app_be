from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para obtener tokens JWT que permite
    login tanto con username como con email.
    """
    
    username_field = 'login'  # Cambiar el nombre del campo para ser más claro
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cambiar la etiqueta del campo para ser más descriptivo
        self.fields[self.username_field] = serializers.CharField(
            help_text=_('Ingrese su nombre de usuario o email')
        )
        self.fields['password'] = serializers.CharField(
            style={'input_type': 'password'},
            trim_whitespace=False
        )
    
    def validate(self, attrs):
        # Obtener las credenciales
        login = attrs.get(self.username_field)
        password = attrs.get('password')
        
        if login and password:
            # Usar el backend personalizado para autenticar
            user = authenticate(
                request=self.context.get('request'),
                username=login,  # El backend personalizado manejará email o username
                password=password
            )
            
            if not user:
                msg = _('No se puede iniciar sesión con las credenciales proporcionadas.')
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                msg = _('La cuenta de usuario está desactivada.')
                raise serializers.ValidationError(msg, code='authorization')
            
            # Verificar si la cuenta está bloqueada
            if hasattr(user, 'cuenta_bloqueada') and user.cuenta_bloqueada:
                msg = _('La cuenta está bloqueada. Contacte al administrador.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Debe incluir "login" y "password".')
            raise serializers.ValidationError(msg, code='authorization')
        
        # Llamar al método padre para generar los tokens JWT
        refresh = self.get_token(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar información adicional al token si es necesario
        token['username'] = user.username
        token['email'] = user.email
        if hasattr(user, 'empleado') and user.empleado:
            token['employee_id'] = user.empleado.id
            token['company'] = user.empleado.empresa.razon_social if user.empleado.empresa else None
        
        return token