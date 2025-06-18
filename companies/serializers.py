from rest_framework import serializers
from .models import Company

class CompanyBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para listados y referencias"""
    class Meta:
        model = Company
        fields = ['id', 'razon_social', 'ruc', 'email', 'activa']

class CompanyDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles y CRUD"""
    active_employees_count = serializers.ReadOnlyField(source='get_active_employees_count')
    
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ['created', 'updated']
    
    def validate_ruc(self, value):
        """Validación personalizada para RUC"""
        if len(value) != 11:
            raise serializers.ValidationError("El RUC debe tener 11 dígitos")
        if not value.isdigit():
            raise serializers.ValidationError("El RUC solo debe contener números")
        return value