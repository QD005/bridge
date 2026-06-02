from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Notification
from .utils import notify_user

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    user = request.user
    queryset = Notification.objects.filter(user=user)

    unread_only = request.query_params.get('unread')
    if unread_only == 'true':
        queryset = queryset.filter(is_read=False)

    limit = int(request.query_params.get('limit', 50))
    offset = int(request.query_params.get('offset', 0))
    
    total = queryset.count()
    notifications = queryset[offset:offset + limit]

    data = [{
        'id': n.id,
        'type': n.notification_type,
        'title': n.title,
        'message': n.message,
        'link': n.link,
        'is_read': n.is_read,
        'read_at': n.read_at.isoformat() if n.read_at else None,
        'created_at': n.created_at.isoformat(),
        'workflow_execution_id': n.workflow_execution_id,
        'service_id': n.service_id,
        'agency_id': n.agency_id,
        'conversation_id': n.conversation_id,
    } for n in notifications]

    return Response({
        'unread_count': Notification.objects.filter(user=user, is_read=False).count(),
        'total': total,
        'offset': offset,
        'limit': limit,
        'notifications': data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_read()
    return Response({'detail': 'Notification marked as read.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_mark_all_read(request):
    Notification.objects.mark_all_read(request.user)
    return Response({'detail': 'All notifications marked as read.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_unread_count(request):
    """Quick poll endpoint for badge count"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'unread_count': count})