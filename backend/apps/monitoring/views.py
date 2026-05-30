from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.agencies.models import Agency
from apps.services.models import ServiceEndpoint
from apps.workflows.models import Workflow
from apps.executions.models import WorkflowExecution, ExecutionStep


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_metrics(request):
    """National Operations Dashboard metrics"""
    user = request.user

    # Base querysets
    agencies = Agency.objects.all() if user.role == 'SUPER_ADMIN' else Agency.objects.filter(status='ACTIVE')
    services = ServiceEndpoint.objects.all() if user.role == 'SUPER_ADMIN' else ServiceEndpoint.objects.filter(status='ACTIVE')
    workflows = Workflow.objects.filter(status='PUBLISHED')
    executions = WorkflowExecution.objects.all()

    # Today's stats
    today = timezone.now().date()
    today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))

    return Response({
        'agencies': {
            'total': agencies.count(),
            'active': agencies.filter(status='ACTIVE').count(),
            'offline': agencies.filter(status='OFFLINE').count(),
            'suspended': agencies.filter(status='SUSPENDED').count(),
        },
        'services': {
            'total': services.count(),
            'online': services.filter(health_status='ONLINE').count(),
            'offline': services.filter(health_status='OFFLINE').count(),
            'degraded': services.filter(health_status='DEGRADED').count(),
        },
        'workflows': {
            'published': workflows.count(),
            'total_executions': executions.count(),
            'running': executions.filter(status='RUNNING').count(),
            'completed_today': executions.filter(status='COMPLETED', completed_at__gte=today_start).count(),
            'failed_today': executions.filter(status='FAILED', completed_at__gte=today_start).count(),
        },
        'executions': {
            'pending': executions.filter(status='PENDING').count(),
            'running': executions.filter(status='RUNNING').count(),
            'waiting': executions.filter(status='WAITING').count(),
            'completed': executions.filter(status='COMPLETED').count(),
            'failed': executions.filter(status='FAILED').count(),
            'cancelled': executions.filter(status='CANCELLED').count(),
        },
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def execution_analytics(request):
    """Detailed execution analytics"""
    days = int(request.query_params.get('days', 7))
    since = timezone.now() - timedelta(days=days)

    executions = WorkflowExecution.objects.filter(started_at__gte=since)

    # Daily breakdown
    daily = {}
    for exec in executions:
        day = exec.started_at.strftime('%Y-%m-%d')
        if day not in daily:
            daily[day] = {'total': 0, 'completed': 0, 'failed': 0}
        daily[day]['total'] += 1
        if exec.status == 'COMPLETED':
            daily[day]['completed'] += 1
        elif exec.status == 'FAILED':
            daily[day]['failed'] += 1

    # Agency breakdown
    agency_stats = {}
    for exec in executions:
        agency = exec.workflow.agency.name
        if agency not in agency_stats:
            agency_stats[agency] = {'total': 0, 'completed': 0, 'failed': 0}
        agency_stats[agency]['total'] += 1
        if exec.status == 'COMPLETED':
            agency_stats[agency]['completed'] += 1
        elif exec.status == 'FAILED':
            agency_stats[agency]['failed'] += 1

    return Response({
        'period_days': days,
        'total_executions': executions.count(),
        'success_rate': round(
            executions.filter(status='COMPLETED').count() / max(executions.count(), 1) * 100, 2
        ),
        'daily_breakdown': daily,
        'agency_breakdown': agency_stats,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def live_activity_feed(request):
    """Recent execution activity for the live feed"""
    limit = int(request.query_params.get('limit', 20))

    executions = WorkflowExecution.objects.select_related(
        'workflow__agency', 'initiated_by'
    ).order_by('-started_at')[:limit]

    feed = []
    for exec in executions:
        feed.append({
            'id': exec.id,
            'workflow': exec.workflow.name,
            'agency': exec.workflow.agency.name,
            'agency_code': exec.workflow.agency.code,
            'status': exec.status,
            'initiated_by': exec.initiated_by.get_full_name() if exec.initiated_by else 'System',
            'started_at': exec.started_at.isoformat(),
            'completed_at': exec.completed_at.isoformat() if exec.completed_at else None,
        })

    return Response(feed)