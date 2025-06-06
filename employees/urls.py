from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeRegistrationViewSet

router = DefaultRouter()
router.register(r'register', EmployeeRegistrationViewSet, basename='employee-register')

urlpatterns = [
    path('', include(router.urls)),
]