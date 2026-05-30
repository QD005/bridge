from django.urls import path
from . import views

urlpatterns = [
    path('', views.audit_log_list, name='audit-list'),
    path('stats/', views.audit_stats, name='audit-stats'),
    path('<int:pk>/', views.audit_log_detail, name='audit-detail'),
]