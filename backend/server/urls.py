from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # App APIs will be added here as we build them
    path('api/auth/', include('apps.accounts.urls')),
    path('api/agencies/', include('apps.agencies.urls')),
    path('api/services/', include('apps.services.urls')),
    path('api/workflows/', include('apps.workflows.urls')),
    path('api/executions/', include('apps.executions.urls')),
    path('api/mock/', include('apps.mocks.urls')),
    path('api/collaboration/', include('apps.collaboration.urls')),
    path('api/monitoring/', include('apps.monitoring.urls')),
    path('api/auditlogs/', include('apps.auditlogs.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)