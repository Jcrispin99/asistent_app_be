from rest_framework import serializers
from .models import Position
from companies.serializers import CompanyBasicSerializer
from departments.serializers import DepartmentBasicSerializer

class PositionBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para listados y referencias"""
    class Meta:
        model = Position
        fields = ['id', 'nombre', 'codigo', 'activo']

class PositionDetailSerializer(serializers.ModelSerializer):
    """Serializer completo con relaciones"""
    empresa = CompanyBasicSerializer(read_only=True)
    empresa_id = serializers.IntegerField(write_only=True)
    departamento = DepartmentBasicSerializer(read_only=True)
    departamento_id = serializers.IntegerField(write_only=True)
    cargo_superior = PositionBasicSerializer(read_only=True)
    cargo_superior_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Campos calculados
    cargos_subordinados = PositionBasicSerializer(source='get_cargos_subordinados', many=True, read_only=True)
    nivel_jerarquico = serializers.ReadOnlyField(source='get_nivel_jerarquico')
    rango_salarial = serializers.ReadOnlyField(source='get_rango_salarial')
    
    class Meta:
        model = Position
        fields = '__all__'
        read_only_fields = ['created', 'updated']
    
    def validate(self, data):
        """Validaciones personalizadas"""
        salario_min = data.get('salario_minimo')
        salario_max = data.get('salario_maximo')
        
        if salario_min and salario_max and salario_max < salario_min:
            raise serializers.ValidationError("El salario máximo debe ser mayor o igual al mínimo")
        
        # Evitar ciclos en jerarquía
        if 'cargo_superior_id' in data and data['cargo_superior_id']:
            if hasattr(self, 'instance') and self.instance and data['cargo_superior_id'] == self.instance.id:
                raise serializers.ValidationError("Un cargo no puede ser superior de sí mismo")
        
        return data