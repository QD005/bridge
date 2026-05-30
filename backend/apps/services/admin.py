from django.contrib import admin
from .models import ServiceEndpoint, ServiceField


class ServiceFieldInline(admin.TabularInline):
    model = ServiceField
    extra = 1
    fields = ['order', 'name', 'label', 'field_type', 'location', 'required', 'placeholder', 'validation_regex']
    ordering = ['order']


@admin.register(ServiceEndpoint)
class ServiceEndpointAdmin(admin.ModelAdmin):
    list_display = ['name', 'agency', 'http_method', 'status', 'health_status', 'version', 'created_at']
    list_filter = ['agency', 'http_method', 'status', 'health_status', 'created_at']
    search_fields = ['name', 'description', 'endpoint_url']
    readonly_fields = ['created_at', 'updated_at', 'health_status']
    inlines = [ServiceFieldInline]


@admin.register(ServiceField)
class ServiceFieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'service', 'field_type', 'location', 'required', 'order']
    list_filter = ['field_type', 'location', 'required', 'service__agency']
    search_fields = ['name', 'label', 'service__name']
    ordering = ['service', 'order']