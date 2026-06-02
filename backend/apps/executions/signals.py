from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import WorkflowExecution, ExecutionStep, StepSubmission


@receiver(post_save, sender=WorkflowExecution)
def workflow_execution_notifications(sender, instance, created, **kwargs):
    """Send notifications on workflow execution status changes."""
    try:
        from apps.notifications.utils import notify_user, notify_multiple
    except ImportError:
        return  # Notifications app not ready yet

    # New workflow created
    if created:
        if instance.initiated_by:
            notify_user(
                user=instance.initiated_by,
                notification_type='WORKFLOW_STARTED',
                title='Workflow Started',
                message=f'Workflow #{instance.id} for {instance.applicant_name or "applicant"} has been initiated.',
                link=f'/requests/{instance.id}',
                workflow_execution=instance
            )
        return

    # Status changed
    if getattr(instance, '_status_changed', False):
        old_status = getattr(instance, '_old_status', None)
        status = instance.status

        # COMPLETED
        if status == 'COMPLETED' and instance.initiated_by:
            notify_user(
                user=instance.initiated_by,
                notification_type='WORKFLOW_COMPLETED',
                title='Workflow Complete',
                message=f'All steps completed for {instance.applicant_name or "Request #" + str(instance.id)}. Ready for certificate issuance.',
                link=f'/requests/{instance.id}',
                workflow_execution=instance
            )

        # REJECTED
        elif status == 'REJECTED' and instance.initiated_by:
            notify_user(
                user=instance.initiated_by,
                notification_type='WORKFLOW_REJECTED',
                title='Workflow Rejected',
                message=f'Request #{instance.id} was rejected. Please review and resubmit.',
                link=f'/requests/{instance.id}',
                workflow_execution=instance
            )

        # CANCELLED - notify all participants
        elif status == 'CANCELLED':
            participants = instance.get_participants()
            if participants:
                notify_multiple(
                    users=participants,
                    notification_type='WORKFLOW_CANCELLED',
                    title='Workflow Cancelled',
                    message=f'Request #{instance.id} has been cancelled.',
                    link=f'/requests/{instance.id}',
                    workflow_execution=instance
                )


@receiver(post_save, sender=ExecutionStep)
def execution_step_notifications(sender, instance, created, **kwargs):
    """Send notifications on step status changes."""
    try:
        from apps.notifications.utils import notify_user
    except ImportError:
        return

    execution = instance.workflow_execution

    # New step created (started)
    if created and instance.status == 'IN_PROGRESS':
        # Notify step assignee if any
        if hasattr(instance.workflow_step, 'assigned_to') and instance.workflow_step.assigned_to:
            notify_user(
                user=instance.workflow_step.assigned_to,
                notification_type='STEP_APPROVAL',
                title=f'Step Started: {instance.step_name}',
                message=f'Step {instance.order} ({instance.step_name}) is now in progress for Request #{execution.id}.',
                link=f'/requests/{execution.id}',
                workflow_execution=execution
            )
        return

    # Status changed
    if getattr(instance, '_status_changed', False):
        old_status = getattr(instance, '_old_status', None)
        status = instance.status

        # FAILED
        if status == 'FAILED' and execution.initiated_by:
            notify_user(
                user=execution.initiated_by,
                notification_type='STEP_FAILED',
                title=f'Step Failed: {instance.step_name}',
                message=f'Step {instance.order} failed. Error: {instance.error_message or "Unknown error"}. Retry or contact support.',
                link=f'/requests/{execution.id}',
                workflow_execution=execution
            )

        # COMPLETED - notify about next step or completion
        elif status == 'COMPLETED':
            next_step = execution.get_next_step()
            
            if next_step and hasattr(next_step.workflow_step, 'assigned_to') and next_step.workflow_step.assigned_to:
                # Notify next assignee
                notify_user(
                    user=next_step.workflow_step.assigned_to,
                    notification_type='STEP_APPROVAL',
                    title='Approval Required',
                    message=f'Step "{next_step.step_name}" is ready for your approval in Request #{execution.id}.',
                    link=f'/requests/{execution.id}',
                    workflow_execution=execution
                )
            elif execution.status == 'COMPLETED' and execution.initiated_by:
                # All steps done - already handled by workflow signal, but backup
                pass


@receiver(post_save, sender=StepSubmission)
def step_submission_notifications(sender, instance, created, **kwargs):
    """Notify on submission success/failure."""
    try:
        from apps.notifications.utils import notify_user
    except ImportError:
        return

    if not created:
        return

    step = instance.execution_step
    execution = step.workflow_execution

    # Submission failed
    if instance.status == 'FAILED' and execution.initiated_by:
        notify_user(
            user=execution.initiated_by,
            notification_type='STEP_FAILED',
            title=f'Submission Failed: {step.step_name}',
            message=f'Record submission failed for Step {step.order}. Error: {instance.error_message or "Service error"}. You can retry with corrected data.',
            link=f'/requests/{execution.id}',
            workflow_execution=execution
        )

    # Submission succeeded but step still has more to do (repeatable)
    elif instance.status == 'SUCCESS' and step.workflow_step.is_repeatable and execution.initiated_by:
        # Optional: notify that more records can be added
        pass