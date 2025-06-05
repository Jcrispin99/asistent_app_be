from django.contrib import admin
from .models import Position

class PositionAdmin(admin.ModelAdmin):
    model = Position
    
    # Campos a mostrar en la lista
    list_display = [
        'nombre',
        'codigo',
        'empresa',
        'departamento',
        'cargo_superior',
        'get_nivel_jerarquico',
        'get_rango_salarial',
        'get_empleados_count',
        'activo',
        'created'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = [
        'empresa',
        'departamento',
        'activo',
        'titulo',
        'created',
        'experiencia'
    ]
    
    # Campos de búsqueda
    search_fields = [
        'nombre',
        'codigo',
        'empresa__razon_social',
        'departamento__nombre',
        'descripcion'
    ]
    
    # Campos de solo lectura
    readonly_fields = [
        'created',
        'updated',
        'get_empleados_count',
        'get_nivel_jerarquico',
        'get_rango_salarial'
    ]
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'descripcion')
        }),
        ('Organización', {
            'fields': ('empresa', 'departamento', 'cargo_superior')
        }),
        ('Requisitos', {
            'fields': ('titulo', 'experiencia')
        }),
        ('Información Salarial', {
            'fields': ('salario_minimo', 'salario_maximo'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadatos', {
            'fields': ('created', 'updated', 'get_nivel_jerarquico', 'get_rango_salarial'),
            'classes': ('collapse',)
        })
    )
    
    # Filtros jerárquicos optimizados
    list_select_related = ['empresa', 'departamento', 'cargo_superior']
    
    # Acciones personalizadas
    actions = ['activar_cargos', 'desactivar_cargos']
    
    def activar_cargos(self, request, queryset):
        """Activa los cargos seleccionados"""
        updated = queryset.update(activo=True)
        self.message_user(
            request,
            f'{updated} cargo(s) activado(s) exitosamente.'
        )
    activar_cargos.short_description = "Activar cargos seleccionados"
    
    def desactivar_cargos(self, request, queryset):
        """Desactiva los cargos seleccionados"""
        updated = queryset.update(activo=False)
        self.message_user(
            request,
            f'{updated} cargo(s) desactivado(s) exitosamente.'
        )
    desactivar_cargos.short_description = "Desactivar cargos seleccionados"
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        return super().get_queryset(request).select_related(
            'empresa', 'departamento', 'cargo_superior'
        )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra los campos relacionados según la empresa seleccionada"""
        if db_field.name == "departamento":
            # Filtrar departamentos por empresa si hay una empresa seleccionada
            if request.resolver_match.kwargs.get('object_id'):
                try:
                    position = Position.objects.get(pk=request.resolver_match.kwargs['object_id'])
                    kwargs["queryset"] = Department.objects.filter(empresa=position.empresa, activo=True)
                except Position.DoesNotExist:
                    pass
        
        if db_field.name == "cargo_superior":
            # Filtrar cargos superiores por departamento
            if request.resolver_match.kwargs.get('object_id'):
                try:
                    position = Position.objects.get(pk=request.resolver_match.kwargs['object_id'])
                    kwargs["queryset"] = Position.objects.filter(
                        departamento=position.departamento, 
                        activo=True
                    ).exclude(pk=position.pk)
                except Position.DoesNotExist:
                    pass
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(Position, PositionAdmin)