from django.urls import path
from . import views

urlpatterns = [
    # Workflow CRUD
    path('', views.workflow_list_create, name='workflow-list-create'),
    path('<int:pk>/', views.workflow_detail, name='workflow-detail'),
    path('<int:pk>/publish/', views.workflow_publish, name='workflow-publish'),
    path('<int:pk>/archive/', views.workflow_archive, name='workflow-archive'),
    path('<int:pk>/clone/', views.workflow_clone, name='workflow-clone'),

    # Step management
    path('<int:workflow_pk>/steps/', views.step_create, name='step-create'),
    path('<int:workflow_pk>/steps/reorder/', views.step_reorder, name='step-reorder'),
    path('<int:workflow_pk>/steps/<int:step_pk>/', views.step_detail, name='step-detail'),
]