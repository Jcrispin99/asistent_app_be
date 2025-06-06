from django.contrib import admin
from django.db import models
from .models import Holiday, HolidayCompany

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 
        'fecha', 
        'tipo', 
        'get_aplicacion_display',
        'obligatorio', 
        'activo',
        'created'
    ]
    
    list_filter = [
        'tipo', 
        'obligatorio', 
        'activo', 
        'es_global',
        'fecha',
        'created'
    ]
    
    search_fields = ['nombre', 'descripcion']
    
    date_hierarchy = 'fecha'
    
    readonly_fields = ['created', 'updated']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'fecha', 'tipo', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('obligatorio', 'es_global', 'activo')
        }),
        ('Auditoría', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        }),
    )
    
    def get_aplicacion_display(self, obj):
        """Muestra si el feriado es global o específico"""
        if obj.es_global:
            return "🌍 Global (Todas las empresas)"
        else:
            # Contar empresas específicas
            count = obj.empresas_especificas.count()
            if count == 0:
                return "⚠️ Sin empresas asignadas"
            elif count == 1:
                empresa = obj.empresas_especificas.first().company.nombre
                return f"🏢 {empresa}"
            else:
                return f"🏢 {count} empresas específicas"
    
    get_aplicacion_display.short_description = "Aplicación"
    get_aplicacion_display.admin_order_field = 'es_global'
    
    def get_queryset(self, request):
        """Optimizar consultas"""
        return super().get_queryset(request).prefetch_related(
            'empresas_especificas__company'
        )
    
    actions = ['marcar_como_activo', 'marcar_como_inactivo', 'duplicar_feriado']
    
    def marcar_como_activo(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} feriados marcados como activos.')
    marcar_como_activo.short_description = "Marcar como activo"
    
    def marcar_como_inactivo(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} feriados marcados como inactivos.')
    marcar_como_inactivo.short_description = "Marcar como inactivo"
    
    def duplicar_feriado(self, request, queryset):
        """Duplicar feriados para el próximo año"""
        from datetime import timedelta
        duplicados = 0
        
        for feriado in queryset:
            # Crear copia para el próximo año
            nueva_fecha = feriado.fecha.replace(year=feriado.fecha.year + 1)
            
            # Verificar que no exista ya
            if not Holiday.objects.filter(
                nombre=feriado.nombre, 
                fecha=nueva_fecha
            ).exists():
                Holiday.objects.create(
                    nombre=feriado.nombre,
                    fecha=nueva_fecha,
                    tipo=feriado.tipo,
                    descripcion=feriado.descripcion,
                    obligatorio=feriado.obligatorio,
                    es_global=feriado.es_global
                )
                duplicados += 1
        
        self.message_user(request, f'{duplicados} feriados duplicados para el próximo año.')
    duplicar_feriado.short_description = "Duplicar para próximo año"


class HolidayCompanyInline(admin.TabularInline):
    """Inline para gestionar empresas específicas desde el Holiday"""
    model = HolidayCompany
    extra = 1
    verbose_name = "Empresa Específica"
    verbose_name_plural = "Empresas Específicas"
    
    def get_formset(self, request, obj=None, **kwargs):
        """Ocultar inline si es feriado global"""
        formset = super().get_formset(request, obj, **kwargs)
        if obj and obj.es_global:
            formset.max_num = 0
            formset.extra = 0
        return formset


@admin.register(HolidayCompany)
class HolidayCompanyAdmin(admin.ModelAdmin):
    """Admin para gestionar relaciones Holiday-Company directamente"""
    list_display = ['holiday', 'company', 'get_fecha', 'get_tipo']
    list_filter = ['holiday__tipo', 'holiday__fecha', 'company']
    search_fields = ['holiday__nombre', 'company__nombre']
    
    def get_fecha(self, obj):
        return obj.holiday.fecha
    get_fecha.short_description = "Fecha"
    get_fecha.admin_order_field = 'holiday__fecha'
    
    def get_tipo(self, obj):
        return obj.holiday.get_tipo_display()
    get_tipo.short_description = "Tipo"
    get_tipo.admin_order_field = 'holiday__tipo'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'holiday', 'company'
        )


# Agregar inline al HolidayAdmin
HolidayAdmin.inlines = [HolidayCompanyInline]
