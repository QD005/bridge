from django.contrib import admin
from .models import WorkflowExecution, ExecutionStep


admin.site.register(WorkflowExecution)
admin.site.register(ExecutionStep)
# class ExecutionStepInline(admin.TabularInline):
#     model = ExecutionStep
#     extra = 0
#     readonly_fields = ['started_at', 'completed_at']
#     fields = ['order', 'workflow_step', 'status', 'response_status_code', 'retry_count', 'approved_by']

# @admin.register(WorkflowExecution)
# class WorkflowExecutionAdmin(admin.ModelAdmin):
#     list_display = ['id', 'workflow', 'status', 'initiated_by', 'started_at', 'completed_at']
#     list_filter = ['status', 'started_at']
#     search_fields = ['workflow__name', 'error_message']
#     inlines = [ExecutionStepInline]
#     readonly_fields = ['started_at', 'completed_at', 'updated_at']

# @admin.register(ExecutionStep)
# class ExecutionStepAdmin(admin.ModelAdmin):
#     list_display = ['workflow_execution', 'order', 'workflow_step', 'status', 'retry_count', 'approved_by']
#     list_filter = ['status', 'workflow_execution__workflow__agency']
#     search_fields = ['workflow_execution__id', 'error_message']