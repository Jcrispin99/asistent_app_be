from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Employee
from .serializers import EmployeeSerializer, EmployeeRegistrationSerializer

User = get_user_model()

class EmployeeRegistrationViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()  # Cambiar de .none() a .all()
    serializer_class = EmployeeRegistrationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'options']  # Agregar métodos
    
    def get_queryset(self):
        # Filtrar empleados por empresa del usuario si es necesario
        return Employee.objects.filter(activo=True)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            employee_data = serializer.save()
            return Response({
                'message': 'Empleado y usuario creados exitosamente',
                'employee': employee_data['employee'],
                'user': employee_data['user']
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            employee_data = serializer.save()
            return Response({
                'message': 'Empleado y usuario actualizados exitosamente',
                'employee': employee_data['employee'],
                'user': employee_data['user']
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
