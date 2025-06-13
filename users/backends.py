from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Backend de autenticación personalizado que permite login
    tanto con username como con email.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None
        
        try:
            # Buscar usuario por username o email
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            # Ejecutar el hash de contraseña por defecto para evitar ataques de timing
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Si hay múltiples usuarios con el mismo email, usar solo username
            try:
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                return None
        
        # Verificar contraseña y si el usuario puede autenticarse
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None