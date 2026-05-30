from django.urls import path
from . import views

urlpatterns = [
    path('', views.conversation_list_create, name='conversation-list-create'),
    path('users/', views.eligible_users, name='eligible-users'),
    path('<int:pk>/', views.conversation_detail, name='conversation-detail'),
    path('<int:conversation_pk>/messages/', views.message_list_create, name='message-list-create'),
    path('<int:conversation_pk>/upload/', views.upload_attachment, name='upload-attachment'),
    path('<int:conversation_pk>/messages/<int:message_pk>/task/', views.update_task_status, name='update-task-status'),
    path('<int:conversation_pk>/messages/<int:message_pk>/pin/', views.message_pin, name='message-pin'),
]