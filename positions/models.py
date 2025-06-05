from django.db import models
from companies.models import Company
from departments.models import Department

class Position(models.Model):
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    codigo = models.CharField(max_length=10, verbose_name='Código')
    descripcion = models.TextField(verbose_name='Descripción', blank=True, null=True)
    empresa = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa')
    departamento = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Departamento')
    cargo_superior = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Cargo Superior')
    salario_minimo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Salario Mínimo', blank=True, null=True)
    salario_maximo = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Salario Máximo', blank=True, null=True)
    titulo = models.BooleanField(default=False, verbose_name='Requiere Título')
    experiencia = models.PositiveIntegerField(default=0, verbose_name='Experiencia Requerida', blank=True, null=True)
    activo = models.BooleanField(default=True, verbose_name='Activo')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated = models.DateTimeField(auto_now=True, verbose_name='Fecha de edición')
    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ['empresa', 'departamento', 'nombre']
        unique_together = ['departamento', 'codigo']

    def __str__(self):
        return f"{self.departamento.nombre} - {self.nombre}"
    
    def get_cargos_subordinados(self):
        """Retorna los cargos que reportan a este cargo"""
        return Position.objects.filter(cargo_superior=self, activo=True)
    
    def get_nivel_jerarquico(self):
        """Retorna el nivel jerárquico del cargo (0 = más alto)"""
        nivel = 0
        superior = self.cargo_superior
        while superior:
            nivel += 1
            superior = superior.cargo_superior
        return nivel
    
    get_nivel_jerarquico.short_description = "Nivel"
    
    def get_rango_salarial(self):
        """Retorna el rango salarial formateado"""
        if self.salario_minimo and self.salario_maximo:
            return f"${self.salario_minimo:,.2f} - ${self.salario_maximo:,.2f}"
        elif self.salario_minimo:
            return f"Desde ${self.salario_minimo:,.2f}"
        elif self.salario_maximo:
            return f"Hasta ${self.salario_maximo:,.2f}"
        return "No definido"
    
    get_rango_salarial.short_description = "Rango Salarial"
    
    def get_empleados_count(self):
        """Retorna el número de empleados en este cargo"""
        return self.employee_set.filter(activo=True).count()