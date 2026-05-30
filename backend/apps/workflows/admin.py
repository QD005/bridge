from django.contrib import admin
from .models import Workflow, WorkflowStep

class WorkflowStepInline(admin.TabularInline):
    model = WorkflowStep
    extra = 0
    fields = ['order', 'step_type', 'name', 'service', 'timeout_seconds', 'requires_approval']
    ordering = ['order']

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'agency', 'status', 'version', 'is_published', 'created_by', 'updated_at']
    list_filter = ['status', 'agency', 'created_at']
    search_fields = ['name', 'description']
    inlines = [WorkflowStepInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'order', 'step_type', 'name', 'service', 'requires_approval']
    list_filter = ['step_type', 'workflow__agency']
    search_fields = ['name', 'workflow__name']
    ordering = ['workflow', 'order']