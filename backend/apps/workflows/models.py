from django.db import models

class Workflow(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    agency = models.ForeignKey(
        'agencies.Agency',
        on_delete=models.CASCADE,
        related_name='workflows'
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='DRAFT')
    version = models.PositiveIntegerField(default=1)
    is_published = models.BooleanField(default=False)

    # Can steps run in any order? If False, they must follow order
    is_sequential = models.BooleanField(default=False, help_text="If True, steps must be completed in order")

    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_workflows'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} v{self.version} ({self.agency.code})"

    def publish(self):
        self.status = 'PUBLISHED'
        self.is_published = True
        self.save(update_fields=['status', 'is_published', 'updated_at'])

    def archive(self):
        self.status = 'ARCHIVED'
        self.is_published = False
        self.save(update_fields=['status', 'is_published', 'updated_at'])


class WorkflowStep(models.Model):
    STEP_TYPES = [
        ('SERVICE', 'Service Call'),
        ('APPROVAL', 'Approval'),
        ('CONDITIONAL', 'Conditional'),
        ('NOTIFICATION', 'Notification'),
        ('MANUAL_REVIEW', 'Manual Review'),
        ('DELAY', 'Delay'),
    ]

    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    service = models.ForeignKey(
        'services.ServiceEndpoint',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='workflow_steps'
    )
    step_type = models.CharField(max_length=50, choices=STEP_TYPES, default='SERVICE')
    name = models.CharField(max_length=255, blank=True, help_text="Display name for this step")

    order = models.PositiveIntegerField(default=0)

    # Can this step be repeated multiple times? (e.g., verify multiple directors)
    is_repeatable = models.BooleanField(default=False, help_text="Allow multiple submissions for this step")
    min_repetitions = models.PositiveIntegerField(default=1, help_text="Minimum required submissions")
    max_repetitions = models.PositiveIntegerField(default=1, help_text="Maximum allowed submissions (0 = unlimited)")

    conditions = models.JSONField(default=dict, blank=True)
    timeout_seconds = models.PositiveIntegerField(default=30)
    retry_policy = models.JSONField(default=dict, blank=True)
    requires_approval = models.BooleanField(default=False)
    approver_roles = models.JSONField(default=list, blank=True)
    config = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        display = self.name or self.get_step_type_display()
        return f"Step {self.order}: {display} ({self.workflow.name})"