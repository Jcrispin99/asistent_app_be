from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView, 
    CreateAPIView, 
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView
)
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg
from django.db.models.functions import TruncDate

from .models import Attendance, QRCode
from .serializers import (
    AttendanceListSerializer,
    AttendanceDetailSerializer,
    MarcarAsistenciaSerializer,
    MisAsistenciasSerializer,
    QRCodeSerializer,
    QRCodeDetailSerializer,
    EstadisticasAsistenciaSerializer
)
from employees.models import Employee


class ListAttendanceView(ListAPIView):
    """Listar todas las asistencias (solo admin/supervisores)"""
    serializer_class = AttendanceListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tipo', 'metodo', 'empleado__empresa']
    search_fields = ['empleado__nombre', 'empleado__apellido', 'empleado__dni']
    ordering_fields = ['fecha_hora', 'empleado__nombre']
    ordering = ['-fecha_hora']
    
    def get_queryset(self):
        queryset = Attendance.objects.select_related(
            'empleado', 'empleado__empresa'
        )
        
        # Filtros por fecha
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_hora__date__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_hora__date__lte=fecha_fin)
            
        return queryset


class AttendanceDetailView(RetrieveUpdateDestroyAPIView):
    """Ver, editar o eliminar una asistencia específica"""
    queryset = Attendance.objects.select_related('empleado', 'empleado__empresa')
    serializer_class = AttendanceDetailSerializer
    permission_classes = [IsAuthenticated]


class MarcarAsistenciaView(CreateAPIView):
    """Endpoint principal para marcar asistencia via QR"""
    serializer_class = MarcarAsistenciaSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Crear la marcación
        attendance = serializer.save()
        
        # Respuesta personalizada
        response_data = {
            'success': True,
            'message': f'Marcación de {attendance.get_tipo_display().lower()} registrada exitosamente',
            'data': {
                'id': attendance.id,
                'tipo': attendance.tipo,
                'tipo_display': attendance.get_tipo_display(),
                'fecha_hora': attendance.fecha_hora,
                'empleado': attendance.empleado.nombre_completo
            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class MisAsistenciasView(ListAPIView):
    """Ver las propias asistencias del empleado autenticado"""
    serializer_class = MisAsistenciasSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['tipo']
    ordering_fields = ['fecha_hora']
    ordering = ['-fecha_hora']
    
    def get_queryset(self):
        try:
            empleado = Employee.objects.get(user=self.request.user)
            queryset = Attendance.objects.filter(empleado=empleado)
            
            # Filtros por fecha
            fecha_inicio = self.request.query_params.get('fecha_inicio')
            fecha_fin = self.request.query_params.get('fecha_fin')
            
            if fecha_inicio:
                queryset = queryset.filter(fecha_hora__date__gte=fecha_inicio)
            if fecha_fin:
                queryset = queryset.filter(fecha_hora__date__lte=fecha_fin)
                
            return queryset
        except Employee.DoesNotExist:
            return Attendance.objects.none()


class QRCodesActivosView(ListAPIView):
    """Listar códigos QR activos para la empresa del empleado"""
    serializer_class = QRCodeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            empleado = Employee.objects.get(user=self.request.user)
            return QRCode.objects.filter(
                empresa=empleado.empresa,
                activo=True
            )
        except Employee.DoesNotExist:
            return QRCode.objects.none()


class ListCreateQRCodeView(ListCreateAPIView):
    """Listar y crear códigos QR (solo admin)"""
    queryset = QRCode.objects.select_related('empresa')
    serializer_class = QRCodeDetailSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['empresa', 'activo']
    search_fields = ['nombre', 'ubicacion', 'codigo_qr']


class QRCodeDetailView(RetrieveUpdateDestroyAPIView):
    """Ver, editar o eliminar un código QR específico"""
    queryset = QRCode.objects.select_related('empresa')
    serializer_class = QRCodeDetailSerializer
    permission_classes = [IsAuthenticated]


class EstadisticasAsistenciaView(APIView):
    """Generar estadísticas de asistencia"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = EstadisticasAsistenciaSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        
        # Obtener parámetros validados
        empleado_id = serializer.validated_data.get('empleado_id')
        fecha_inicio = serializer.validated_data.get('fecha_inicio')
        fecha_fin = serializer.validated_data.get('fecha_fin')
        empresa_id = serializer.validated_data.get('empresa_id')
        
        # Construir queryset base
        queryset = Attendance.objects.select_related('empleado')
        
        # Aplicar filtros
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)
        if empresa_id:
            queryset = queryset.filter(empleado__empresa_id=empresa_id)
        if fecha_inicio:
            queryset = queryset.filter(fecha_hora__date__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_hora__date__lte=fecha_fin)
        
        # Calcular estadísticas
        total_marcaciones = queryset.count()
        total_entradas = queryset.filter(tipo='entrada').count()
        total_salidas = queryset.filter(tipo='salida').count()
        
        # Marcaciones por día
        marcaciones_por_dia = queryset.annotate(
            fecha=TruncDate('fecha_hora')
        ).values('fecha').annotate(
            total=Count('id'),
            entradas=Count('id', filter=Q(tipo='entrada')),
            salidas=Count('id', filter=Q(tipo='salida'))
        ).order_by('fecha')
        
        # Marcaciones por método
        marcaciones_por_metodo = queryset.values('metodo').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Empleados más activos (si no se filtró por empleado específico)
        empleados_activos = []
        if not empleado_id:
            empleados_activos = queryset.values(
                'empleado__id',
                'empleado__nombre',
                'empleado__apellido'
            ).annotate(
                total_marcaciones=Count('id')
            ).order_by('-total_marcaciones')[:10]
        
        response_data = {
            'resumen': {
                'total_marcaciones': total_marcaciones,
                'total_entradas': total_entradas,
                'total_salidas': total_salidas,
                'periodo': {
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin
                }
            },
            'marcaciones_por_dia': list(marcaciones_por_dia),
            'marcaciones_por_metodo': list(marcaciones_por_metodo),
            'empleados_mas_activos': list(empleados_activos)
        }
        
        return Response(response_data)


class ResumenDiarioView(APIView):
    """Resumen de asistencia del día actual para el empleado"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            empleado = Employee.objects.get(user=request.user)
            hoy = timezone.now().date()
            
            # Marcaciones del día
            marcaciones_hoy = Attendance.objects.filter(
                empleado=empleado,
                fecha_hora__date=hoy
            ).order_by('fecha_hora')
            
            # Última marcación
            ultima_marcacion = marcaciones_hoy.last()
            
            # Determinar próxima acción
            proxima_accion = 'entrada'
            if ultima_marcacion and ultima_marcacion.tipo == 'entrada':
                proxima_accion = 'salida'
            
            # Calcular horas trabajadas (aproximado)
            horas_trabajadas = 0
            if marcaciones_hoy.count() >= 2:
                entradas = marcaciones_hoy.filter(tipo='entrada')
                salidas = marcaciones_hoy.filter(tipo='salida')
                
                for i, entrada in enumerate(entradas):
                    if i < salidas.count():
                        salida = salidas[i]
                        delta = salida.fecha_hora - entrada.fecha_hora
                        horas_trabajadas += delta.total_seconds() / 3600
            
            response_data = {
                'fecha': hoy,
                'empleado': empleado.nombre_completo,
                'marcaciones_hoy': MisAsistenciasSerializer(marcaciones_hoy, many=True).data,
                'ultima_marcacion': {
                    'tipo': ultima_marcacion.tipo if ultima_marcacion else None,
                    'hora': ultima_marcacion.fecha_hora.time() if ultima_marcacion else None
                },
                'proxima_accion': proxima_accion,
                'horas_trabajadas_aproximadas': round(horas_trabajadas, 2),
                'total_marcaciones': marcaciones_hoy.count()
            }
            
            return Response(response_data)
            
        except Employee.DoesNotExist:
            return Response(
                {'error': 'No se encontró el empleado asociado al usuario'},
                status=status.HTTP_404_NOT_FOUND
            )
