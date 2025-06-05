from django.db import models
from django.core.validators import MinLengthValidator

class Company(models.Model):
    razon_social=models.CharField(max_length=100, verbose_name='Razón Social')
    ruc = models.CharField(max_length=11, verbose_name='RUC')
    direccion = models.TextField(verbose_name='Dirección')
    telefono = models.CharField(max_length=13, verbose_name='Teléfono')
    email = models.EmailField(verbose_name='Email')
    logo = models.ImageField(upload_to='companies/logos', null=True, blank=True, verbose_name='Logo')
    firma = models.ImageField(upload_to='companies/firmas', null=True, blank=True, verbose_name='Firma')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated = models.DateTimeField(auto_now=True, verbose_name='Fecha de edición')
    activa = models.BooleanField(default=True, verbose_name='¿Está activa?',)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['razon_social']
    def __str__(self):
        return self.razon_social

    def get_active_employees_count(self):
        """Retorna el número de empleados activos de la empresa"""
        return self.employee_set.filter(activo=True).count()