from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_list_create, name='service-list-create'),
    path('<int:pk>/', views.service_detail, name='service-detail'),
    path('<int:pk>/schema/', views.service_schema, name='service-schema'),
    path('<int:pk>/preview/', views.service_preview, name='service-preview'),
    path('<int:pk>/execute/', views.service_execute, name='service-execute'),
    path('<int:pk>/test/', views.service_test, name='service-test'),
    path('<int:pk>/fields/', views.service_field_create, name='service-field-create'),
    path('<int:pk>/fields/<int:field_pk>/', views.service_field_detail, name='service-field-detail'),
]