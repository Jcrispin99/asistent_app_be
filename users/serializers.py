from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    employee_info = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'is_active', 'date_joined', 'employee_info']
        read_only_fields = ['date_joined']
    
    def get_employee_info(self, obj):
        if hasattr(obj, 'empleado') and obj.empleado:
            return {
                'dni': obj.empleado.dni,
                'nombres': obj.empleado.nombres,
                'apellidos': obj.empleado.apellidos,
                'empresa': obj.empleado.empresa.razon_social if obj.empleado.empresa else None
            }
        return None