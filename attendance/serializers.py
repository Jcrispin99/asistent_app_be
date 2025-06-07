from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Attendance, QRCode
from employees.models import Employee
from companies.models import Company


class QRCodeSerializer(serializers.ModelSerializer):
    """Serializer básico para códigos QR"""
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    
    class Meta:
        model = QRCode
        fields = [
            'id', 'codigo_qr', 'nombre', 'ubicacion', 
            'activo', 'empresa', 'empresa_nombre'
        ]
        read_only_fields = ['id']


class QRCodeDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para códigos QR (admin)"""
    empresa_nombre = serializers.CharField(source='empresa.razon_social', read_only=True)
    
    class Meta:
        model = QRCode
        fields = '__all__'
        read_only_fields = ['id', 'created']


class AttendanceListSerializer(serializers.ModelSerializer):
    """Serializer para listar asistencias"""
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    empleado_dni = serializers.CharField(source='empleado.dni', read_only=True)
    empresa_nombre = serializers.CharField(source='empleado.empresa.razon_social', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    metodo_display = serializers.CharField(source='get_metodo_display', read_only=True)
    fecha = serializers.DateField(read_only=True)
    hora = serializers.TimeField(read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'empleado', 'empleado_nombre', 'empleado_dni', 
            'empresa_nombre', 'fecha_hora', 'fecha', 'hora',
            'tipo', 'tipo_display', 'metodo', 'metodo_display',
            'latitud', 'longitud', 'dispositivo_info', 'observaciones'
        ]


class AttendanceDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para asistencias"""
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    empleado_dni = serializers.CharField(source='empleado.dni', read_only=True)
    empresa_nombre = serializers.CharField(source='empleado.empresa.razon_social', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    metodo_display = serializers.CharField(source='get_metodo_display', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['id', 'created']


class MarcarAsistenciaSerializer(serializers.Serializer):
    """Serializer para marcar asistencia via QR"""
    codigo_qr = serializers.CharField(max_length=100)
    latitud = serializers.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        required=False, 
        allow_null=True
    )
    longitud = serializers.DecimalField(
        max_digits=11, 
        decimal_places=8, 
        required=False, 
        allow_null=True
    )
    dispositivo_info = serializers.CharField(
        max_length=200, 
        required=False, 
        allow_blank=True
    )
    
    def validate_codigo_qr(self, value):
        """Validar que el código QR existe y está activo"""
        try:
            qr_code = QRCode.objects.get(codigo_qr=value, activo=True)
            return value
        except QRCode.DoesNotExist:
            raise serializers.ValidationError(
                "Código QR inválido o inactivo"
            )
    
    def validate(self, attrs):
        """Validaciones adicionales"""
        # Obtener el empleado del contexto (usuario autenticado)
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Usuario no autenticado"
            )
        
        try:
            empleado = Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            raise serializers.ValidationError(
                "No se encontró el empleado asociado al usuario"
            )
        
        # Validar que el empleado pertenece a la empresa del QR
        qr_code = QRCode.objects.get(codigo_qr=attrs['codigo_qr'])
        if empleado.empresa != qr_code.empresa:
            raise serializers.ValidationError(
                "No tienes permisos para marcar en esta ubicación"
            )
        
        # Determinar tipo de marcación (entrada/salida)
        hoy = timezone.now().date()
        ultima_marcacion = Attendance.objects.filter(
            empleado=empleado,
            fecha_hora__date=hoy
        ).order_by('-fecha_hora').first()
        
        if not ultima_marcacion or ultima_marcacion.tipo == 'salida':
            tipo_marcacion = 'entrada'
        else:
            tipo_marcacion = 'salida'
        
        # Validar que no haya marcaciones muy recientes (evitar duplicados)
        hace_5_minutos = timezone.now() - timedelta(minutes=5)
        marcacion_reciente = Attendance.objects.filter(
            empleado=empleado,
            fecha_hora__gte=hace_5_minutos
        ).exists()
        
        if marcacion_reciente:
            raise serializers.ValidationError(
                "Ya has marcado recientemente. Espera al menos 5 minutos."
            )
        
        attrs['empleado'] = empleado
        attrs['tipo'] = tipo_marcacion
        attrs['metodo'] = 'qr_movil'
        
        return attrs
    
    def create(self, validated_data):
        """Crear la marcación de asistencia"""
        return Attendance.objects.create(**validated_data)


class MisAsistenciasSerializer(serializers.ModelSerializer):
    """Serializer para que el empleado vea sus propias asistencias"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    metodo_display = serializers.CharField(source='get_metodo_display', read_only=True)
    fecha = serializers.DateField(read_only=True)
    hora = serializers.TimeField(read_only=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'fecha_hora', 'fecha', 'hora',
            'tipo', 'tipo_display', 'metodo', 'metodo_display',
            'observaciones'
        ]


class EstadisticasAsistenciaSerializer(serializers.Serializer):
    """Serializer para estadísticas de asistencia"""
    empleado_id = serializers.IntegerField(required=False)
    fecha_inicio = serializers.DateField(required=False)
    fecha_fin = serializers.DateField(required=False)
    empresa_id = serializers.IntegerField(required=False)
    
    def validate(self, attrs):
        """Validar fechas"""
        fecha_inicio = attrs.get('fecha_inicio')
        fecha_fin = attrs.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise serializers.ValidationError(
                    "La fecha de inicio no puede ser mayor a la fecha fin"
                )
        
        return attrs