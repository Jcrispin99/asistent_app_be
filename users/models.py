from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from employees.models import Employee


class CustomUser(AbstractUser):
    empleado = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Empleado Asociado'
    )
    
    # Campos específicos del sistema
    ultimo_acceso_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='Última IP')
    intentos_fallidos = models.PositiveIntegerField(default=0, verbose_name='Intentos Fallidos')
    cuenta_bloqueada = models.BooleanField(default=False, verbose_name='Cuenta Bloqueada')
    fecha_bloqueo = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Bloqueo')
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        if self.empleado:
            return f"{self.username} ({self.empleado.nombre_completo})"
        return self.username
    
    @property
    def nombre_completo(self):
        if self.empleado:
            return self.empleado.nombre_completo
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @property
    def empresa(self):
        return self.empleado.empresa if self.empleado else None
    
    @property
    def es_empleado(self):
        return self.empleado is not None
    
    def tiene_acceso_empresa(self, empresa):
        if self.is_superuser:
            return True
        return self.empleado and self.empleado.empresa == empresa
    
    def bloquear_cuenta(self):
        """Bloquea la cuenta del usuario"""
        self.cuenta_bloqueada = True
        self.fecha_bloqueo = timezone.now()
        self.save()
    
    def desbloquear_cuenta(self):
        """Desbloquea la cuenta del usuario"""
        self.cuenta_bloqueada = False
        self.intentos_fallidos = 0
        self.fecha_bloqueo = None
        self.save()