from rest_framework import serializers
from .models import Department
from companies.serializers import CompanyBasicSerializer

class DepartmentBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para listados y referencias"""
    class Meta:
        model = Department
        fields = ['id', 'nombre', 'codigo', 'activo']

class DepartmentDetailSerializer(serializers.ModelSerializer):
    """Serializer completo con relaciones"""
    empresa = CompanyBasicSerializer(read_only=True)
    empresa_id = serializers.IntegerField(write_only=True)
    dep_padre = DepartmentBasicSerializer(read_only=True)
    dep_padre_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    # Campos calculados
    subdepartamentos = DepartmentBasicSerializer(source='get_subdepartamentos', many=True, read_only=True)
    nivel_jerarquia = serializers.ReadOnlyField(source='get_nivel_jerarquia')
    empleados_count = serializers.ReadOnlyField(source='get_empleados_count')

    class Meta:
        model = Department
        fields = '__all__'
        read_only_fields = ['created', 'updated']

    def validate(self, data):
        """Validación para evitar ciclos en jerarquía"""
        if 'dep_padre_id' in data and data['dep_padre_id']:
            # Evitar que un departamento sea padre de sí mismo
            if hasattr(self, 'instance') and self.instance and data['dep_padre_id'] == self.instance.id:
                raise serializers.ValidationError("Un departamento no puede ser padre de sí mismo")
        return data