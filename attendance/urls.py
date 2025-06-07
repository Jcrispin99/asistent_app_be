from django.urls import path
from .views import (
    ListAttendanceView,
    AttendanceDetailView,
    MarcarAsistenciaView,
    MisAsistenciasView,
    QRCodesActivosView,
    ListCreateQRCodeView,
    QRCodeDetailView,
    EstadisticasAsistenciaView,
    ResumenDiarioView
)

app_name = 'attendance'

urlpatterns = [
    # Endpoints principales para empleados
    path('marcar/', MarcarAsistenciaView.as_view(), name='marcar-asistencia'),
    path('mis-marcaciones/', MisAsistenciasView.as_view(), name='mis-asistencias'),
    path('resumen-diario/', ResumenDiarioView.as_view(), name='resumen-diario'),
    path('qr-activos/', QRCodesActivosView.as_view(), name='qr-activos'),
    
    # Endpoints administrativos - Asistencias
    path('', ListAttendanceView.as_view(), name='list-attendance'),
    path('<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('estadisticas/', EstadisticasAsistenciaView.as_view(), name='estadisticas'),
    
    # Endpoints administrativos - Códigos QR
    path('qr-codes/', ListCreateQRCodeView.as_view(), name='list-create-qr'),
    path('qr-codes/<int:pk>/', QRCodeDetailView.as_view(), name='qr-detail'),
]