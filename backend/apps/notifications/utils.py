from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from .models import Notification

def notify_user(user, notification_type, title, message, link=None, 
                workflow_execution=None, service=None, agency=None, 
                conversation=None, exclude_socket=False):
    """
    Create notification in DB and push via WebSocket if user is online.
    
    Args:
        user: User instance
        notification_type: One of Notification.TYPE_CHOICES
        title: Short title
        message: Full message
        link: Frontend route (e.g. "/requests/123")
        workflow_execution: Related WorkflowExecution instance (optional)
        service: Related ServiceEndpoint instance (optional)
        agency: Related Agency instance (optional)
        conversation: Related Conversation instance (optional)
        exclude_socket: If True, only save to DB (useful for bulk operations)
    """
    
    # Create DB record
    notif = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        workflow_execution=workflow_execution,
        service=service,
        agency=agency,
        conversation=conversation,
    )
    
    # Send WebSocket push
    if not exclude_socket:
        channel_layer = get_channel_layer()
        try:
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    "type": "notification_push",
                    "data": {
                        "id": notif.id,
                        "type": notification_type,
                        "title": title,
                        "message": message,
                        "link": link,
                        "is_read": False,
                        "created_at": notif.created_at.isoformat(),
                        "workflow_execution_id": workflow_execution.id if workflow_execution else None,
                        "service_id": service.id if service else None,
                        "agency_id": agency.id if agency else None,
                        "conversation_id": conversation.id if conversation else None,
                    }
                }
            )
        except Exception as e:
            # Log but don't fail if Redis/Channels is down
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"WebSocket notification failed for user {user.id}: {e}")
    
    return notif


def notify_multiple(users, notification_type, title, message, link=None, **kwargs):
    """
    Bulk notify multiple users (e.g. all admins when service goes down).
    """
    notifications = []
    for user in users:
        notif = notify_user(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            exclude_socket=True,  # Bulk - skip individual WS for performance
            **kwargs
        )
        notifications.append(notif)
    
    # Optional: Send one broadcast to all users' groups
    channel_layer = get_channel_layer()
    for user in users:
        try:
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    "type": "notification_push",
                    "data": {
                        "type": notification_type,
                        "title": title,
                        "message": message,
                        "link": link,
                        "is_read": False,
                        "created_at": timezone.now().isoformat(),
                        "bulk": True,
                    }
                }
            )
        except Exception:
            pass
    
    return notifications


def notify_admins(notification_type, title, message, link=None, **kwargs):
    """
    Notify all admin/staff users.
    """
    from apps.accounts.models import User
    admins = User.objects.filter(role__in=['ADMIN', 'STAFF'], is_active=True)
    return notify_multiple(admins, notification_type, title, message, link, **kwargs)