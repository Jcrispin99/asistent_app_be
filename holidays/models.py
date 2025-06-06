from turtle import update
from django.db import models
from companies.models import Company

class Holiday(models.Model):
    HOLIDAY_TYPES = [
        ('nacional', 'Feriado Nacional'),
        ('local', 'Feriado Local'),
        ('empresa', 'Día de la Empresa'),
        ('religioso', 'Feriado Religioso'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Feriado")
    fecha = models.DateField(verbose_name="Fecha")
    tipo = models.CharField(max_length=20, choices=HOLIDAY_TYPES, default='nacional')
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    obligatorio = models.BooleanField(default=True, verbose_name="Es Obligatorio")
    
    # CAMBIO: Feriados globales por defecto
    es_global = models.BooleanField(default=True, verbose_name="Aplica a Todas las Empresas")
    
    # Campos de auditoría
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Feriado"
        verbose_name_plural = "Feriados"
        ordering = ['fecha']
        unique_together = ['fecha', 'nombre']  # No duplicar por fecha/nombre
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha}"
    
    @classmethod
    def get_holidays_for_company(cls, company, fecha_inicio=None, fecha_fin=None):
        """
        Obtener feriados que aplican a una empresa específica
        """
        queryset = cls.objects.filter(activo=True)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        
        # Feriados globales + feriados específicos de la empresa
        return queryset.filter(
            models.Q(es_global=True) | 
            models.Q(es_global=False, empresas_especificas=company)
        ).distinct()

# Tabla intermedia para feriados específicos por empresa
class HolidayCompany(models.Model):
    holiday = models.ForeignKey(
        Holiday, 
        on_delete=models.CASCADE,
        related_name='empresas_especificas'
    )
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        related_name='feriados_especificos'
    )
    
    class Meta:
        unique_together = ['holiday', 'company']
        verbose_name = "Feriado por Empresa"
        verbose_name_plural = "Feriados por Empresa"