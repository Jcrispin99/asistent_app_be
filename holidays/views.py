from .serializers import HolidaySerializer, HolidayListSerializer
from .models import Holiday
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class ListHolidaysView(ListAPIView, CreateAPIView):
    """GET /api/v1/holidays/ - Listar feriados
       POST /api/v1/holidays/ - Crear feriado"""
    allowed_methods = ['GET', 'POST']
    queryset = Holiday.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'obligatorio', 'es_global', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['fecha', 'nombre', 'created']
    ordering = ['fecha']
    
    def get_serializer_class(self):
        """Usar serializer simplificado para GET, completo para POST"""
        if self.request.method == 'GET':
            return HolidayListSerializer
        return HolidaySerializer
    
    def get_queryset(self):
        """Filtros personalizados"""
        queryset = Holiday.objects.all()
        
        # Filtro por año
        year = self.request.query_params.get('year')
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(fecha__year=year)
            except ValueError:
                pass
        
        # Filtro por mes
        month = self.request.query_params.get('month')
        if month:
            try:
                month = int(month)
                queryset = queryset.filter(fecha__month=month)
            except ValueError:
                pass
        
        return queryset

class HolidayDetailView(RetrieveUpdateDestroyAPIView):
    """GET /api/v1/holidays/{id}/ - Detalle de feriado
       PUT /api/v1/holidays/{id}/ - Actualizar feriado
       DELETE /api/v1/holidays/{id}/ - Eliminar feriado"""
    allowed_methods = ['GET', 'PUT', 'PATCH', 'DELETE']
    serializer_class = HolidaySerializer
    queryset = Holiday.objects.all()
    permission_classes = [IsAuthenticated]
