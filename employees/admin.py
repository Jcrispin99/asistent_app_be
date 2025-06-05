from django.contrib import admin
from .models import Employee

class EmployeeAdmin(admin.ModelAdmin):
    model = Employee

    # Campos a mostrar en la lista
    list_display = [
        'codigo_empleado',
        'apellidos',
        'nombres',
        'dni',
        'empresa',
        'departamento',
        'cargo',
        'shift_type',
        'rest_day',
        'get_edad',
        'get_antiguedad',
        'salario_actual',
        'activo',
        'fecha_ingreso'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = [
        'empresa',
        'departamento',
        'cargo',
        'shift_type',
        'rest_day',
        'activo',
        'fecha_ingreso',
        'fecha_cese'
    ]
    
    # Campos de búsqueda
    search_fields = [
        'nombres',
        'apellidos',
        'dni',
        'codigo_empleado',
        'email_personal',
        'telefono'
    ]
    
    # Campos de solo lectura
    readonly_fields = [
        'created',
        'updated',
        'get_edad',
        'get_antiguedad',
        'get_email_corporativo',
        'nombre_completo'
    ]
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Información Personal', {
            'fields': (
                ('nombres', 'apellidos'),
                ('dni', 'fecha_nacimiento'),
                ('telefono', 'email_personal'),
                'direccion'
            )
        }),
        ('Información Laboral', {
            'fields': (
                'codigo_empleado',
                ('empresa', 'departamento', 'cargo'),
                ('fecha_ingreso', 'salario_actual'),
                ('shift_type', 'rest_day')
            )
        }),
        ('Archivos', {
            'fields': ('foto', 'firma'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': (
                'activo',
                ('fecha_cese', 'motivo_cese')
            )
        }),
        ('Información Calculada', {
            'fields': (
                'nombre_completo',
                'get_edad',
                'get_antiguedad',
                'get_email_corporativo'
            ),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        })
    )
    
    # Filtros jerárquicos optimizados
    list_select_related = ['empresa', 'departamento', 'cargo']
    
    # Acciones personalizadas
    actions = ['activar_empleados', 'desactivar_empleados', 'generar_reporte']
    
    def activar_empleados(self, request, queryset):
        """Activa los empleados seleccionados"""
        updated = queryset.update(activo=True, fecha_cese=None, motivo_cese=None)
        self.message_user(
            request,
            f'{updated} empleado(s) activado(s) exitosamente.'
        )
    activar_empleados.short_description = "Activar empleados seleccionados"
    
    def desactivar_empleados(self, request, queryset):
        """Desactiva los empleados seleccionados"""
        from datetime import date
        updated = queryset.update(activo=False, fecha_cese=date.today())
        self.message_user(
            request,
            f'{updated} empleado(s) desactivado(s) exitosamente.'
        )
    desactivar_empleados.short_description = "Desactivar empleados seleccionados"
    
    def generar_reporte(self, request, queryset):
        """Genera reporte de empleados seleccionados"""
        count = queryset.count()
        self.message_user(
            request,
            f'Reporte generado para {count} empleado(s). (Funcionalidad por implementar)'
        )
    generar_reporte.short_description = "Generar reporte de empleados"
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        return super().get_queryset(request).select_related(
            'empresa', 'departamento', 'cargo'
        )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra los campos relacionados según las selecciones"""
        if db_field.name == "departamento":
            # Filtrar departamentos por empresa si hay una empresa seleccionada
            if request.resolver_match.kwargs.get('object_id'):
                try:
                    employee = Employee.objects.get(pk=request.resolver_match.kwargs['object_id'])
                    kwargs["queryset"] = Department.objects.filter(
                        empresa=employee.empresa, activo=True
                    )
                except Employee.DoesNotExist:
                    pass
        
        if db_field.name == "cargo":
            # Filtrar cargos por departamento
            if request.resolver_match.kwargs.get('object_id'):
                try:
                    employee = Employee.objects.get(pk=request.resolver_match.kwargs['object_id'])
                    kwargs["queryset"] = Position.objects.filter(
                        departamento=employee.departamento, activo=True
                    )
                except Employee.DoesNotExist:
                    pass
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        
admin.site.register(Employee, EmployeeAdmin)
