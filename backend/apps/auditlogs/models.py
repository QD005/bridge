from django.db import models

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('READ', 'Read / Query'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('LOGIN_FAILED', 'Login Failed'),
        ('API_CALL', 'API Call'),
        ('WORKFLOW_STEP', 'Workflow Step'),
        ('TASK_UPDATE', 'Task Update'),
        ('PIN', 'Pin/Unpin'),
        ('FILE_UPLOAD', 'File Upload'),
        ('EXPORT', 'Data Export'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
    ]

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs'
    )
    
    # Action metadata
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUCCESS')
    
    # What was affected
    entity_type = models.CharField(max_length=100, help_text="Model name or endpoint name, e.g. 'ServiceEndpoint', 'login', 'nira-verify'")
    entity_id = models.CharField(max_length=100, blank=True, help_text="Primary key of affected object")
    entity_name = models.CharField(max_length=255, blank=True, help_text="Human-readable name, e.g. 'Verify Citizen Identity'")
    
    # Request details
    http_method = models.CharField(max_length=10, blank=True)
    url = models.URLField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Before/After for updates
    previous_data = models.JSONField(default=dict, blank=True, help_text="Snapshot before change")
    new_data = models.JSONField(default=dict, blank=True, help_text="Snapshot after change")
    
    # Error info for failures
    error_message = models.TextField(blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)
    
    # Description
    description = models.TextField(blank=True, help_text="Human-readable summary")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['entity_type', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.action} by {self.user.email if self.user else 'Anonymous'} at {self.created_at}"