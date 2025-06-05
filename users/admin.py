from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    list_display = [
        'username',
        'get_nombre_completo',
        'get_empresa',
        'is_active',
        'is_staff',
        'cuenta_bloqueada',
        'last_login'
    ]
    
    list_filter = [
        'is_active',
        'is_staff',
        'cuenta_bloqueada',
        'empleado__empresa'
    ]
    
    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email',
        'empleado__nombres',
        'empleado__apellidos'
    ]
    
    # Para EDITAR usuarios existentes
    fieldsets = UserAdmin.fieldsets + (
        ('Información del Empleado', {
            'fields': ('empleado',)
        }),
        ('Seguridad', {
            'fields': (
                'ultimo_acceso_ip',
                'intentos_fallidos',
                'cuenta_bloqueada',
                'fecha_bloqueo'
            )
        })
    )
    
    # Para CREAR nuevos usuarios - ESTO ES LO QUE FALTA
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información del Empleado', {
            'fields': ('empleado',)
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
    )
    
    def get_nombre_completo(self, obj):
        return obj.nombre_completo
    get_nombre_completo.short_description = 'Nombre Completo'
    
    def get_empresa(self, obj):
        return obj.empresa.razon_social if obj.empresa else 'Sin empresa'
    get_empresa.short_description = 'Empresa'

admin.site.register(CustomUser, CustomUserAdmin)
