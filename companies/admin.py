from django.contrib import admin
from .models import Company

class CompanyAdmin(admin.ModelAdmin):
    model = Company
    
  # Campos que se muestran en la lista
    list_display = [
        'razon_social', 
        'ruc', 
        'telefono', 
        'email', 
        'activa',
        'logo',
        'get_active_employees_count',
        'created'
    ]
    
    # Campos por los que se puede filtrar
    list_filter = [
        'activa',
        'created'
    ]
    
    # Campos de búsqueda
    search_fields = [
        'razon_social',
        'ruc',
        'email'
    ]
    
    # Campos de solo lectura
    readonly_fields = [
        'created',
        'updated'
    ]
    
    # Organización de campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('razon_social', 'ruc')
        }),
        ('Contacto', {
            'fields': ('direccion', 'telefono', 'email')
        }),
        ('Imagen', {
            'fields': ('logo',)
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
    )
    
    # Acciones personalizadas
    actions = ['activar_empresas', 'desactivar_empresas']
    
    def activar_empresas(self, request, queryset):
        """Activa las empresas seleccionadas"""
        updated = queryset.update(activa=True)
        self.message_user(
            request,
            f'{updated} empresa(s) activada(s) exitosamente.'
        )
    activar_empresas.short_description = "Activar empresas seleccionadas"
    
    def desactivar_empresas(self, request, queryset):
        """Desactiva las empresas seleccionadas"""
        updated = queryset.update(activa=False)
        self.message_user(
            request,
            f'{updated} empresa(s) desactivada(s) exitosamente.'
        )
    desactivar_empresas.short_description = "Desactivar empresas seleccionadas"

admin.site.register(Company, CompanyAdmin)