from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.services.models import ServiceEndpoint, ServiceField
from apps.workflows.models import Workflow, WorkflowStep
from apps.executions.models import WorkflowExecution, ExecutionStep, StepSubmission
from apps.collaboration.models import Message, Conversation
from .utils import log_action

User = get_user_model()

# Models to track
TRACKED_MODELS = {
    'ServiceEndpoint': 'Service',
    'ServiceField': 'Service Field',
    'Workflow': 'Workflow',
    'WorkflowStep': 'Workflow Step',
    'WorkflowExecution': 'Request',
    'ExecutionStep': 'Execution Step',
    'StepSubmission': 'Submission',
    'Message': 'Chat Message',
    'Conversation': 'Conversation',
    'User': 'User Account',
}

def get_current_user():
    """Try to get current user from thread local."""
    from threading import local
    _thread_locals = local()
    return getattr(_thread_locals, 'user', None)

@receiver(pre_save)
def capture_pre_save(sender, instance, **kwargs):
    """Capture old data before update."""
    if sender.__name__ not in TRACKED_MODELS:
        return
    
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._audit_old_data = {
                f.name: getattr(old, f.name)
                for f in sender._meta.fields
                if not f.is_relation and f.name not in ['created_at', 'updated_at', 'password']
            }
        except sender.DoesNotExist:
            instance._audit_old_data = {}

@receiver(post_save)
def log_create_update(sender, instance, created, **kwargs):
    """Log all creates and updates."""
    if sender.__name__ not in TRACKED_MODELS:
        return
    
    user = get_current_user()
    action = 'CREATE' if created else 'UPDATE'
    entity_name = TRACKED_MODELS.get(sender.__name__, sender.__name__)
    
    # Get display name
    name = ''
    if hasattr(instance, 'name'):
        name = instance.name
    elif hasattr(instance, 'title'):
        name = instance.title
    elif hasattr(instance, 'content'):
        name = instance.content[:50]
    elif hasattr(instance, 'email'):
        name = instance.email
    
    old_data = getattr(instance, '_audit_old_data', {})
    
    # Build new data snapshot
    new_data = {}
    for f in sender._meta.fields:
        if not f.is_relation and f.name not in ['created_at', 'updated_at', 'password']:
            val = getattr(instance, f.name, None)
            try:
                # JSON serializable check
                json.dumps(val)
                new_data[f.name] = val
            except (TypeError, ValueError):
                new_data[f.name] = str(val) if val is not None else None
    
    log_action(
        user=user,
        action=action,
        status='SUCCESS',
        entity_type=sender.__name__,
        entity_id=instance.pk,
        entity_name=name,
        previous_data=old_data,
        new_data=new_data,
        description=f"{action} {entity_name} '{name}' (ID: {instance.pk})"
    )

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    """Log all deletions."""
    if sender.__name__ not in TRACKED_MODELS:
        return
    
    user = get_current_user()
    entity_name = TRACKED_MODELS.get(sender.__name__, sender.__name__)
    
    name = ''
    if hasattr(instance, 'name'):
        name = instance.name
    elif hasattr(instance, 'title'):
        name = instance.title
    elif hasattr(instance, 'email'):
        name = instance.email
    
    log_action(
        user=user,
        action='DELETE',
        status='SUCCESS',
        entity_type=sender.__name__,
        entity_id=instance.pk,
        entity_name=name,
        description=f"DELETE {entity_name} '{name}' (ID: {instance.pk})"
    )