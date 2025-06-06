from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Department
from .serializers import DepartmentBasicSerializer, DepartmentDetailSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related('empresa').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'created']
    ordering = ['nombre']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DepartmentBasicSerializer
        return DepartmentDetailSerializer
    
    def get_queryset(self):
        """
        Optimización: usar select_related para evitar N+1 queries
        """
        return Department.objects.select_related(
            'empresa', 'dep_padre'
        ).prefetch_related('department_set')
