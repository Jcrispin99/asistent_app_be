from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Position
from .serializers import PositionBasicSerializer, PositionDetailSerializer

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.select_related('empresa', 'departamento').all()
    Permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'departamento', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'created']
    ordering = ['nombre']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PositionBasicSerializer
        return PositionDetailSerializer
