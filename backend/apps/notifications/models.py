from django.db import models

class Notification(models.Model):
    TYPE_CHOICES = [
        ('WORKFLOW_COMPLETED', 'Workflow Completed'),
        ('WORKFLOW_FAILED', 'Workflow Failed'),
        ('STEP_APPROVAL', 'Step Approval Required'),
        ('SERVICE_DOWN', 'Service Down'),
        ('AGENCY_OFFLINE', 'Agency Offline'),
        ('EXECUTION_WAITING', 'Execution Waiting'),
        ('SYSTEM_ALERT', 'System Alert'),
    ]

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()

    # Related entities
    workflow_execution = models.ForeignKey(
        'executions.WorkflowExecution',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='notifications'
    )
    service = models.ForeignKey(
        'services.ServiceEndpoint',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type}: {self.title}"