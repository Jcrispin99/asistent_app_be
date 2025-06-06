from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListHolidaysView.as_view(), name='holidays-list'),
    path('<int:pk>/', views.HolidayDetailView.as_view(), name='holiday-detail'),
]