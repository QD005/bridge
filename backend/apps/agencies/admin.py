from django.contrib import admin
from .models import Agency

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'status', 'authentication_type', 'base_url', 'created_by', 'created_at']
    list_filter = ['status', 'authentication_type', 'created_at']
    search_fields = ['name', 'code', 'contact_email', 'base_url']
    readonly_fields = ['created_at', 'updated_at']