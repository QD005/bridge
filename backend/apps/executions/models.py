from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

class WorkflowExecution(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]

    workflow = models.ForeignKey(
        'workflows.Workflow',
        on_delete=models.CASCADE,
        related_name='executions'
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')

    # Applicant / requester information
    applicant_name = models.CharField(max_length=255, blank=True, help_text="Name of the citizen/applicant")
    applicant_contact = models.CharField(max_length=255, blank=True, help_text="Phone or email of applicant")
    
    # The initial application data (company name, director NINs, etc.)
    payload = models.JSONField(default=dict, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    initiated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='initiated_executions'
    )

    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Request #{self.id} — {self.workflow.name} ({self.status})"

    def save(self, *args, **kwargs):
        # Track status change for notifications
        if self.pk:
            old = WorkflowExecution.objects.filter(pk=self.pk).first()
            if old and old.status != self.status:
                self._status_changed = True
                self._old_status = old.status
        super().save(*args, **kwargs)

    def get_next_step(self):
        """Get the next pending step in order."""
        return self.steps.filter(
            status__in=['PENDING', 'WAITING']
        ).order_by('order').first()

    def get_participants(self):
        """Get all users involved in this execution."""
        users = set()
        if self.initiated_by:
            users.add(self.initiated_by)
        for step in self.steps.all():
            if step.approved_by:
                users.add(step.approved_by)
        return list(users)


class ExecutionStep(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('SKIPPED', 'Skipped'),
    ]

    workflow_execution = models.ForeignKey(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    workflow_step = models.ForeignKey(
        'workflows.WorkflowStep',
        on_delete=models.CASCADE,
        related_name='execution_steps'
    )

    order = models.PositiveIntegerField(default=0)

    # Status of this step overall (not individual submissions)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')

    # Officer notes / approval
    officer_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_execution_steps'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"ExecStep {self.order} — {self.workflow_step.name or self.workflow_step.step_type} ({self.status})"

    @property
    def step_name(self):
        return self.workflow_step.name or self.workflow_step.step_type

    @property
    def step_type(self):
        return self.workflow_step.step_type

    @property
    def service(self):
        return self.workflow_step.service

    def save(self, *args, **kwargs):
        # Track status change for notifications
        if self.pk:
            old = ExecutionStep.objects.filter(pk=self.pk).first()
            if old and old.status != self.status:
                self._status_changed = True
                self._old_status = old.status
        super().save(*args, **kwargs)


class StepSubmission(models.Model):
    """Each individual submission/run of a workflow step"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    execution_step = models.ForeignKey(
        ExecutionStep,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    # The data that was submitted to the service
    submission_data = models.JSONField(default=dict, blank=True)

    # The response received from the service
    response_data = models.JSONField(default=dict, blank=True)
    response_status_code = models.PositiveIntegerField(null=True, blank=True)

    # Status of this individual submission
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')

    # Error if any
    error_message = models.TextField(blank=True)

    # Who made this submission
    submitted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Submission #{self.id} for Step {self.execution_step.order}"