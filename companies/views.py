from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Company
from .serializers import CompanyBasicSerializer, CompanyDetailSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activa'] 
    search_fields = ['razon_social', 'direccion']  
    ordering_fields = ['razon_social', 'created']  
    ordering = ['razon_social'] 
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyBasicSerializer
        return CompanyDetailSerializer
