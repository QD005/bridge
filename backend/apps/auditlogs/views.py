from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import AuditLog
from .serializers import AuditLogSerializer, AuditLogListSerializer


def get_audit_queryset(user):
    if user.role == 'SUPER_ADMIN':
        return AuditLog.objects.all()
    elif user.role == 'AUDITOR':
        return AuditLog.objects.all()
    elif user.agency:
        # Show logs for user's agency + their own actions
        return AuditLog.objects.filter(
            Q(user__agency=user.agency) | Q(user=user)
        ).distinct()
    else:
        return AuditLog.objects.filter(user=user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_log_list(request):
    user = request.user
    queryset = get_audit_queryset(user)
    
    # Filters
    action = request.query_params.get('action')
    status_filter = request.query_params.get('status')
    entity_type = request.query_params.get('entity')
    user_id = request.query_params.get('user')
    search = request.query_params.get('search')
    date_from = request.query_params.get('from')
    date_to = request.query_params.get('to')
    
    if action:
        queryset = queryset.filter(action=action.upper())
    if status_filter:
        queryset = queryset.filter(status=status_filter.upper())
    if entity_type:
        queryset = queryset.filter(entity_type__icontains=entity_type)
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)
    if search:
        queryset = queryset.filter(
            Q(description__icontains=search) |
            Q(entity_name__icontains=search) |
            Q(error_message__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    
    # Pagination
    limit = int(request.query_params.get('limit', 50))
    offset = int(request.query_params.get('offset', 0))
    total = queryset.count()
    queryset = queryset[offset:offset + limit]
    
    serializer = AuditLogListSerializer(queryset, many=True)
    return Response({
        'results': serializer.data,
        'total': total,
        'limit': limit,
        'offset': offset
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_log_detail(request, pk):
    user = request.user
    log = get_object_or_404(AuditLog, pk=pk)
    
    if user.role not in ['SUPER_ADMIN', 'AUDITOR']:
        if log.user != user and (not log.user or log.user.agency != user.agency):
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AuditLogSerializer(log)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audit_stats(request):
    """Dashboard stats for audit logs."""
    user = request.user
    queryset = get_audit_queryset(user)
    
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    
    stats = {
        'total_actions': queryset.count(),
        'today': queryset.filter(created_at__date=today).count(),
        'last_7_days': queryset.filter(created_at__date__gte=last_7_days).count(),
        'failed_actions': queryset.filter(status='FAILED').count(),
        'by_action': list(queryset.values('action').annotate(count=Count('action')).order_by('-count')),
        'by_status': list(queryset.values('status').annotate(count=Count('status'))),
        'top_users': list(queryset.exclude(user=None).values('user__email', 'user__first_name', 'user__last_name').annotate(count=Count('id')).order_by('-count')[:5]),
    }
    
    return Response(stats)