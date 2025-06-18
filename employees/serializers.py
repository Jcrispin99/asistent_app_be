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
        # Verificar si ya existe un empleado con este DNI
        request = self.context.get('request')
        if request and request.method in ['PUT', 'PATCH']:
            # Si es una actualización, excluir el empleado actual de la validación
            instance = self.instance
            employee_exists = Employee.objects.filter(dni=value).exclude(id=instance.id).exists()
            user_exists = User.objects.filter(username=value).exclude(empleado=instance).exists()
        else:
            # Si es una creación, verificar si ya existe
            employee_exists = Employee.objects.filter(dni=value).exists()
            user_exists = User.objects.filter(username=value).exists()
        
        if employee_exists:
            raise serializers.ValidationError("Ya existe un empleado con este DNI.")
        if user_exists:
            raise serializers.ValidationError("Ya existe un usuario con este DNI como nombre de usuario.")
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
    
    @transaction.atomic
    def update(self, instance, validated_data):
        # Extraer campos específicos del usuario
        password = validated_data.pop('password', None)
        validated_data.pop('confirm_password', None)
        user_email = validated_data.pop('email', None)
        is_active = validated_data.pop('is_active', None)
        
        # Obtener el usuario asociado al empleado
        try:
            user = User.objects.get(empleado=instance)
        except User.DoesNotExist:
            user = None
        
        # Actualizar el empleado
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Si existe un usuario asociado, actualizarlo
        if user:
            # Actualizar username si cambió el DNI
            if instance.dni != user.username:
                user.username = instance.dni
            
            # Actualizar otros campos del usuario si se proporcionaron
            if user_email:
                user.email = user_email
            if is_active is not None:
                user.is_active = is_active
            if password:
                user.set_password(password)
            
            # Actualizar nombres
            user.first_name = instance.nombres
            user.last_name = instance.apellidos
            user.save()
        
        # Retornar datos estructurados para la vista
        return {
            'employee': {
                'id': instance.id,
                'dni': instance.dni,
                'nombres': instance.nombres,
                'apellidos': instance.apellidos,
                'codigo_empleado': instance.codigo_empleado,
                'empresa': instance.empresa.razon_social,
                'departamento': instance.departamento.nombre,
                'cargo': instance.cargo.nombre
            },
            'user': {
                'id': user.id if user else None,
                'username': user.username if user else None,
                'email': user.email if user else None,
                'is_active': user.is_active if user else None
            } if user else None
        }

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'