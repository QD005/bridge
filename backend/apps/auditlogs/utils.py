from .models import AuditLog

def log_action(
    user=None,
    action='OTHER',
    status='SUCCESS',
    entity_type='',
    entity_id='',
    entity_name='',
    http_method='',
    url='',
    ip_address=None,
    user_agent='',
    previous_data=None,
    new_data=None,
    error_message='',
    status_code=None,
    description=''
):
    """Universal logging function. Call this from anywhere."""
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            status=status,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else '',
            entity_name=entity_name,
            http_method=http_method,
            url=url,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else '',
            previous_data=previous_data or {},
            new_data=new_data or {},
            error_message=error_message,
            status_code=status_code,
            description=description
        )
    except Exception as e:
        # Never let logging break the main flow
        print(f"Audit log failed: {e}")