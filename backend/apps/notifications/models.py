from django.db import models
from django.utils import timezone

class NotificationManager(models.Manager):
    def unread(self):
        return self.filter(is_read=False)
    
    def for_user(self, user):
        return self.filter(user=user)
    
    def mark_all_read(self, user):
        return self.filter(user=user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )

class Notification(models.Model):
    TYPE_CHOICES = [
        ('WORKFLOW_STARTED', 'Workflow Started'),
        ('WORKFLOW_COMPLETED', 'Workflow Completed'),
        ('WORKFLOW_FAILED', 'Workflow Failed'),
        ('WORKFLOW_REJECTED', 'Workflow Rejected'),
        ('WORKFLOW_CANCELLED', 'Workflow Cancelled'),
        ('STEP_COMPLETED', 'Step Completed'),
        ('STEP_FAILED', 'Step Failed'),
        ('STEP_APPROVAL', 'Step Approval Required'),
        ('TASK_ASSIGNED', 'Task Assigned'),
        ('TASK_UPDATED', 'Task Updated'),
        ('NEW_MESSAGE', 'New Message'),
        ('MENTION', 'Mention'),
        ('SERVICE_DOWN', 'Service Down'),
        ('SERVICE_UP', 'Service Up'),
        ('AGENCY_OFFLINE', 'Agency Offline'),
        ('AGENCY_ONLINE', 'Agency Online'),
        ('EXECUTION_WAITING', 'Execution Waiting'),
        ('CERTIFICATE_ISSUED', 'Certificate Issued'),
        ('SYSTEM_ALERT', 'System Alert'),
        ('FAILED_LOGIN', 'Failed Login Attempt'),
        ('PASSWORD_CHANGED', 'Password Changed'),
    ]

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True, help_text="Frontend route e.g. /requests/123")

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
    conversation = models.ForeignKey(
        'collaboration.Conversation',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = NotificationManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])