from rest_framework import serializers
from .models import Holiday

class HolidaySerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Holiday
        fields = '__all__'
        read_only_fields = ['created', 'updated']
    
    def validate_fecha(self, value):
        """Validación personalizada para fecha"""
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("No se pueden crear feriados en fechas pasadas")
        return value
    
    def validate(self, data):
        """Validación a nivel de objeto"""
        nombre = data.get('nombre')
        fecha = data.get('fecha')
        
        if nombre and fecha:
            queryset = Holiday.objects.filter(nombre=nombre, fecha=fecha)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError(
                    "Ya existe un feriado con este nombre en la misma fecha"
                )
        
        return data

class HolidayListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Holiday
        fields = ['id', 'nombre', 'fecha', 'tipo', 'tipo_display', 'obligatorio', 'es_global', 'activo']