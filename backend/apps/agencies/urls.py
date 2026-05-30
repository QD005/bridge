from django.urls import path
from . import views

urlpatterns = [
    path('', views.agency_list_create, name='agency-list-create'),
    path('<int:pk>/', views.agency_detail, name='agency-detail'),
    path('<int:pk>/disable/', views.agency_disable, name='agency-disable'),
    path('<int:pk>/test/', views.agency_test_connectivity, name='agency-test'),
]