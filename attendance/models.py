from django.db import models
from employees.models import Employee
from datetime import datetime
from django.utils import timezone

class Attendance(models.Model):
    TIPO_MARCACION = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]
    
    METODO_MARCACION = [
        ('qr_movil', 'QR desde Móvil'),
        ('manual_seguridad', 'Manual desde Seguridad'),
        ('web_admin', 'Web Admin'),
    ]
    
    empleado = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        verbose_name='Empleado'
    )
    
    fecha_hora = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha y Hora'
    )
    
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_MARCACION,
        verbose_name='Tipo de Marcación'
    )
    
    metodo = models.CharField(
        max_length=20,
        choices=METODO_MARCACION,
        default='qr_movil',
        verbose_name='Método de Marcación'
    )
    
    # Para geolocalización (opcional)
    latitud = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        null=True, 
        blank=True,
        verbose_name='Latitud'
    )
    
    longitud = models.DecimalField(
        max_digits=11, 
        decimal_places=8, 
        null=True, 
        blank=True,
        verbose_name='Longitud'
    )
    
    # Para identificar desde qué dispositivo/lugar se marcó
    dispositivo_info = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Info del Dispositivo'
    )
    
    # Usuario que registró (para marcaciones manuales)
    registrado_por = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Registrado por'
    )
    
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Marcación de Asistencia'
        verbose_name_plural = 'Marcaciones de Asistencia'
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.get_tipo_display()} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
    
    @property
    def fecha(self):
        """Retorna solo la fecha"""
        return self.fecha_hora.date()
    
    @property
    def hora(self):
        """Retorna solo la hora"""
        return self.fecha_hora.time()


class QRCode(models.Model):
    """Modelo para gestionar códigos QR de las empresas/ubicaciones"""
    empresa = models.ForeignKey(
        'companies.Company',
        on_delete=models.CASCADE,
        verbose_name='Empresa'
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del Punto'
    )
    
    codigo_qr = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Código QR'
    )
    
    ubicacion = models.CharField(
        max_length=200,
        verbose_name='Ubicación'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    class Meta:
        verbose_name = 'Código QR'
        verbose_name_plural = 'Códigos QR'
        ordering = ['empresa', 'nombre']
    
    def __str__(self):
        return f"{self.empresa.razon_social} - {self.nombre}"