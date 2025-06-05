from django.db import models
from companies.models import Company

class Department(models.Model):
    nombre = models.CharField(max_length=100, verbose_name='Nombre del departamento')
    codigo = models.CharField(max_length=10, verbose_name='Código del departamento' )
    descripcion = models.TextField(verbose_name='Descripción del departamento', blank=True, null=True)
    empresa = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    dep_padre = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Departamento padre')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated = models.DateTimeField(auto_now=True, verbose_name='Fecha de edición')
    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['empresa', 'nombre']
        unique_together = ['empresa', 'codigo']
    def __str__(self):
        return f"{self.empresa.razon_social} - {self.nombre}"

    def get_subdepartamentos(self):
        """Retorna los subdepartamentos de este departamento"""
        return Department.objects.filter(dep_padre=self, activo=True)
    
    def get_nivel_jerarquia(self):
        """Retorna el nivel en la jerarquía (0 = raíz)"""
        nivel = 0
        padre = self.dep_padre
        while padre:
            nivel += 1
            padre = padre.dep_padre
        return nivel
    
    get_nivel_jerarquia.short_description = "Nivel"
    
    def get_empleados_count(self):
        """Retorna el número de empleados en este departamento"""
        return self.employee_set.filter(activo=True).count()