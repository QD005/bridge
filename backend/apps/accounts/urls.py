from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.profile, name='profile'),
    path('users/', views.user_list, name='user-list'),
    path('users/<int:pk>/', views.user_detail, name='user-detail'),
]