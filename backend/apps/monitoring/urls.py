from django.urls import path
from . import views

urlpatterns = [
    path('metrics/', views.dashboard_metrics, name='dashboard-metrics'),
    path('analytics/', views.execution_analytics, name='execution-analytics'),
    path('activity/', views.live_activity_feed, name='live-activity'),
]