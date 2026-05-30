from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'action', 'status', 'entity_type', 'entity_name', 'http_method', 'status_code', 'created_at']
    list_filter = ['action', 'status', 'entity_type', 'created_at']
    search_fields = ['user__email', 'entity_name', 'description', 'error_message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'