from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Employee

User = get_user_model()

class EmployeeRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    # Campos adicionales para el usuario
    email = serializers.EmailField(required=False, help_text="Email para el usuario (si es diferente al personal)")
    is_active = serializers.BooleanField(default=True, help_text="Usuario activo")
    
    class Meta:
        model = Employee
        fields = [
            # Datos personales del empleado
            'nombres', 'apellidos', 'dni', 'fecha_nacimiento',
            'telefono', 'email_personal', 'direccion', 
            
            # Datos laborales del empleado
            'codigo_empleado', 'fecha_ingreso', 'salario_actual', 
            'empresa', 'departamento', 'cargo', 
            'shift_type', 'rest_day', 
            
            # Archivos
            'foto', 'firma',
            
            # Campos para el usuario
            'password', 'confirm_password', 'email', 'is_active'
        ]
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return data
    
    def validate_dni(self, value):
        # Verificar que no exista empleado con este DNI
        if Employee.objects.filter(dni=value).exists():
            raise serializers.ValidationError("Ya existe un empleado con este DNI.")
        
        # Verificar que no exista usuario con este username (DNI)
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este DNI.")
        
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        # Extraer campos específicos del usuario
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        user_email = validated_data.pop('email', None)
        is_active = validated_data.pop('is_active', True)
        
        # Crear empleado
        employee = Employee.objects.create(**validated_data)
        
        # Determinar email para el usuario
        email_usuario = user_email or employee.email_personal or f"{employee.dni}@empresa.com"
        
        # Crear usuario con DNI como username
        user = User.objects.create_user(
            username=employee.dni,
            password=password,
            email=email_usuario,
            first_name=employee.nombres,
            last_name=employee.apellidos,
            is_active=is_active,
            empleado=employee
        )
        
        # Retornar datos estructurados para la vista
        return {
            'employee': {
                'id': employee.id,
                'dni': employee.dni,
                'nombres': employee.nombres,
                'apellidos': employee.apellidos,
                'codigo_empleado': employee.codigo_empleado,
                'empresa': employee.empresa.razon_social,  # Cambiar de .nombre a .razon_social
                'departamento': employee.departamento.nombre,
                'cargo': employee.cargo.nombre
            },
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active
            }
        }

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'