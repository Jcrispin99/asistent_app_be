from django.contrib import admin
from .models import Attendance, QRCode
from django.utils.html import format_html


class AttendanceAdmin(admin.ModelAdmin):
    model = Attendance
    list_display = [
        'empleado',
        'fecha_hora',
        'get_tipo_color',
        'get_metodo_color',
        'registrado_por'
    ]
    
    list_filter = [
        'tipo',
        'metodo',
        'fecha_hora',
        'empleado__empresa',
        'empleado__departamento'
    ]
    
    search_fields = [
        'empleado__nombres',
        'empleado__apellidos',
        'empleado__dni',
        'empleado__codigo_empleado'
    ]
    
    readonly_fields = ['created']
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'empleado',
                'fecha_hora',
                ('tipo', 'metodo')
            )
        }),
        ('Ubicación (Opcional)', {
            'fields': (
                ('latitud', 'longitud'),
            ),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': (
                'dispositivo_info',
                'registrado_por',
                'observaciones'
            ),
            'classes': ('collapse',)
        })
    )
    
    def get_tipo_color(self, obj):
        color = 'green' if obj.tipo == 'entrada' else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_tipo_display()
        )
    get_tipo_color.short_description = 'Tipo'
    
    def get_metodo_color(self, obj):
        colors = {
            'qr_movil': 'blue',
            'manual_seguridad': 'orange',
            'web_admin': 'purple'
        }
        color = colors.get(obj.metodo, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_metodo_display()
        )
    get_metodo_color.short_description = 'Método'


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = [
        'empresa',
        'nombre',
        'codigo_qr',
        'ubicacion',
        'activo',
        'created'
    ]
    
    list_filter = [
        'empresa',
        'activo',
        'created'
    ]
    
    search_fields = [
        'nombre',
        'codigo_qr',
        'ubicacion',
        'empresa__razon_social'
    ]
    
    readonly_fields = ['created']
admin.site.register(Attendance, AttendanceAdmin)