from django.contrib import admin
from .models import Department

class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    
    # Campos a mostrar en la lista
    list_display = [
        'nombre',
        'codigo', 
        'empresa',
        'dep_padre',
        'get_nivel_jerarquia',
        'get_empleados_count',
        'activo',
        'created'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = [
        'empresa',
        'activo',
        'created',
        'dep_padre'
    ]
    
    # Campos de búsqueda
    search_fields = [
        'nombre',
        'codigo',
        'empresa__razon_social',
        'descripcion'
    ]
    
    # Campos de solo lectura
    readonly_fields = [
        'created',
        'updated',
        'get_empleados_count',
        'get_nivel_jerarquia'
    ]
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'codigo', 'descripcion')
        }),
        ('Organización', {
            'fields': ('empresa', 'dep_padre')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Metadatos', {
            #'fields': ('created', 'updated', 'get_empleados_count', 'get_nivel_jerarquia'),
            'fields': ('created', 'updated', 'get_nivel_jerarquia'),
            'classes': ('collapse',)
        })
    )
    
    # Filtros jerárquicos
    list_select_related = ['empresa', 'dep_padre']
    
    # Acciones personalizadas
    actions = ['activar_departamentos', 'desactivar_departamentos']
    
    def activar_departamentos(self, request, queryset):
        """Activa los departamentos seleccionados"""
        updated = queryset.update(activo=True)
        self.message_user(
            request,
            f'{updated} departamento(s) activado(s) exitosamente.'
        )
    activar_departamentos.short_description = "Activar departamentos seleccionados"
    
    def desactivar_departamentos(self, request, queryset):
        """Desactiva los departamentos seleccionados"""
        updated = queryset.update(activo=False)
        self.message_user(
            request,
            f'{updated} departamento(s) desactivado(s) exitosamente.'
        )
    desactivar_departamentos.short_description = "Desactivar departamentos seleccionados"
    
    def get_queryset(self, request):
        """Optimiza las consultas"""
        return super().get_queryset(request).select_related('empresa', 'dep_padre')

admin.site.register(Department, DepartmentAdmin)