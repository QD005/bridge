from django.db import models

class Conversation(models.Model):
    TYPE_CHOICES = [
        ('DIRECT', 'Direct Message'),
        ('WORKFLOW', 'Workflow Discussion'),
        ('EXECUTION', 'Execution Discussion'),
        ('INCIDENT', 'Incident Discussion'),
        ('AGENCY', 'Agency Coordination'),
        ('APPROVAL', 'Approval Review'),
    ]

    workflow = models.ForeignKey(
        'workflows.Workflow',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='conversations'
    )
    execution = models.ForeignKey(
        'executions.WorkflowExecution',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='conversations'
    )
    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='conversations'
    )

    conversation_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='WORKFLOW')
    title = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    # Participants for direct/group messaging
    participants = models.ManyToManyField(
        'accounts.User',
        related_name='conversations',
        blank=True
    )

    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.get_conversation_type_display()} #{self.id}"


class Message(models.Model):
    MESSAGE_TYPES = [
        ('TEXT', 'Text'),
        ('TASK', 'Task Assignment'),
        ('FILE', 'File'),
        ('SYSTEM', 'System'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    TASK_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sent_messages'
    )

    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='TEXT')
    
    # Task assignment fields
    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_tasks'
    )
    task_status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='PENDING')
    task_due_date = models.DateTimeField(null=True, blank=True)
    is_pinned = models.BooleanField(default=False, help_text="Pinned to top of conversation like WhatsApp")

    mentions = models.JSONField(default=list, blank=True, help_text="List of user IDs mentioned")

    # Attachments stored as array of file metadata dicts: [{"name": "file.pdf", "url": "/media/...", "size": 1234}]
    attachments = models.JSONField(default=list, blank=True)

    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='NORMAL')
    is_edited = models.BooleanField(default=False)
    
    # Read receipts: list of user IDs who have read this message
    read_by = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg #{self.id} by {self.sender.email if self.sender else 'Unknown'}"

    @property
    def is_task(self):
        return self.message_type == 'TASK'

    @property
    def read_count(self):
        return len(self.read_by)