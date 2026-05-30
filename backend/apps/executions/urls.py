from django.urls import path
from . import views

urlpatterns = [
    path('', views.execution_list_create, name='execution-list-create'),
    path('<int:pk>/', views.execution_detail, name='execution-detail'),
    path('<int:pk>/cancel/', views.execution_cancel, name='execution-cancel'),
    path('<int:pk>/complete/', views.execution_complete, name='execution-complete'),
    path('<int:pk>/reject/', views.execution_reject, name='execution-reject'),
    path('<int:pk>/steps/<int:step_pk>/submit/', views.execution_step_submit, name='execution-step-submit'),
    path('<int:pk>/steps/<int:step_pk>/complete/', views.execution_step_complete, name='execution-step-complete'),
]