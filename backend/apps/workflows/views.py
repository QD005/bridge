from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q

from .models import Workflow, WorkflowStep
from .serializers import (
    WorkflowListSerializer, WorkflowDetailSerializer,
    WorkflowCreateSerializer, WorkflowStepSerializer
)
from .permissions import CanManageWorkflow


def get_workflow_queryset(user):
    if user.role == 'SUPER_ADMIN':
        return Workflow.objects.all().select_related('agency', 'created_by').prefetch_related('steps')
    elif user.role in ['AGENCY_ADMIN', 'DEVELOPER', 'OPERATIONS_OFFICER']:
        q = Q(status='PUBLISHED')
        if user.agency_id:
            q |= Q(agency=user.agency)
        return Workflow.objects.filter(q).select_related('agency', 'created_by').prefetch_related('steps')
    else:
        return Workflow.objects.filter(status='PUBLISHED').select_related('agency', 'created_by').prefetch_related('steps')


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def workflow_list_create(request):
    user = request.user

    if request.method == 'GET':
        queryset = get_workflow_queryset(user)
        agency_id = request.query_params.get('agency')
        status_filter = request.query_params.get('status')
        search = request.query_params.get('search')

        if agency_id:
            queryset = queryset.filter(agency_id=agency_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))

        serializer = WorkflowListSerializer(queryset, many=True)
        return Response(serializer.data)

    # POST — create workflow
    if user.role not in ['SUPER_ADMIN', 'AGENCY_ADMIN', 'DEVELOPER']:
        return Response(
            {'detail': 'You do not have permission to create workflows.'},
            status=status.HTTP_403_FORBIDDEN
        )

    data = request.data.copy()
    if user.role != 'SUPER_ADMIN':
        data['agency_id'] = user.agency_id

    serializer = WorkflowCreateSerializer(data=data)
    if serializer.is_valid():
        workflow = serializer.save(created_by=user)
        return Response(
            WorkflowDetailSerializer(workflow).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, CanManageWorkflow])
def workflow_detail(request, pk):
    workflow = get_object_or_404(
        Workflow.objects.select_related('agency', 'created_by').prefetch_related('steps__service__agency'),
        pk=pk
    )
    user = request.user

    if request.method == 'GET':
        if user.role == 'SUPER_ADMIN' or workflow.status == 'PUBLISHED' or user.agency == workflow.agency:
            serializer = WorkflowDetailSerializer(workflow)
            return Response(serializer.data)
        return Response({'detail': 'Not authorized to view this workflow.'}, status=status.HTTP_403_FORBIDDEN)

    can_modify = (
        user.role == 'SUPER_ADMIN' or
        (user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == workflow.agency)
    )
    if not can_modify:
        return Response(
            {'detail': 'Not authorized to modify this workflow.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Cannot modify published workflows directly — must create new version or unpublish
    # if workflow.status == 'PUBLISHED' and request.method in ['PUT', 'PATCH']:
    #     return Response(
    #         {'detail': 'Cannot modify a published workflow. Archive it first or create a new version.'},
    #         status=status.HTTP_400_BAD_REQUEST
    #     )

    if request.method in ['PUT', 'PATCH']:
        data = request.data.copy()
        if user.role != 'SUPER_ADMIN':
            data.pop('agency_id', None)

        serializer = WorkflowDetailSerializer(workflow, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        workflow.delete()
        return Response({'detail': 'Workflow deleted.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def workflow_publish(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk)
    user = request.user

    can_publish = (
        user.role == 'SUPER_ADMIN' or
        (user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == workflow.agency)
    )
    if not can_publish:
        return Response(
            {'detail': 'Not authorized to publish this workflow.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if workflow.status == 'PUBLISHED':
        return Response(
            {'detail': 'Workflow is already published.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if workflow.steps.count() == 0:
        return Response(
            {'detail': 'Cannot publish a workflow with no steps.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    workflow.publish()
    return Response({
        'detail': f'Workflow "{workflow.name}" published successfully.',
        'workflow': WorkflowDetailSerializer(workflow).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def workflow_archive(request, pk):
    workflow = get_object_or_404(Workflow, pk=pk)
    user = request.user

    can_archive = (
        user.role == 'SUPER_ADMIN' or
        (user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == workflow.agency)
    )
    if not can_archive:
        return Response(
            {'detail': 'Not authorized to archive this workflow.'},
            status=status.HTTP_403_FORBIDDEN
        )

    workflow.archive()
    return Response({
        'detail': f'Workflow "{workflow.name}" archived.',
        'workflow': WorkflowDetailSerializer(workflow).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def workflow_clone(request, pk):
    workflow = get_object_or_404(Workflow.objects.prefetch_related('steps'), pk=pk)
    user = request.user

    can_clone = (
        user.role == 'SUPER_ADMIN' or
        (user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == workflow.agency) or
        workflow.status == 'PUBLISHED'
    )
    if not can_clone:
        return Response(
            {'detail': 'Not authorized to clone this workflow.'},
            status=status.HTTP_403_FORBIDDEN
        )

    with transaction.atomic():
        # Create new workflow as draft
        new_workflow = Workflow.objects.create(
            name=f"{workflow.name} (Copy)",
            description=workflow.description,
            agency=workflow.agency,
            status='DRAFT',
            version=workflow.version + 1,
            is_published=False,
            created_by=user
        )

        # Clone all steps
        for step in workflow.steps.all():
            WorkflowStep.objects.create(
                workflow=new_workflow,
                service=step.service,
                step_type=step.step_type,
                name=step.name,
                order=step.order,
                conditions=step.conditions,
                timeout_seconds=step.timeout_seconds,
                retry_policy=step.retry_policy,
                requires_approval=step.requires_approval,
                approver_roles=step.approver_roles,
                config=step.config
            )

    return Response({
        'detail': f'Workflow cloned as "{new_workflow.name}".',
        'workflow': WorkflowDetailSerializer(new_workflow).data
    }, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────────────
# WORKFLOW STEP MANAGEMENT
# ─────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def step_create(request, workflow_pk):
    workflow = get_object_or_404(Workflow, pk=workflow_pk)
    user = request.user

    can_modify = (
        user.role == 'SUPER_ADMIN' or
        (user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == workflow.agency)
    )
    if not can_modify:
        return Response(
            {'detail': 'Not authorized to modify this workflow.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if workflow.status == 'PUBLISHED':
        return Response(
            {'detail': 'Cannot modify steps of a published workflow.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    data = request.data.copy()
    data['workflow'] = workflow.id

    # Auto-assign next order if not provided
    if 'order' not in data or data['order'] is None:
        last_order = workflow.steps.aggregate(max_order=models.Max('order'))['max_order'] or 0
        data['order'] = last_order + 1

    serializer = WorkflowStepSerializer(data=data)
    if serializer.is_valid():
        step = serializer.save()
        return Response(WorkflowStepSerializer(step).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def step_detail(request, workflow_pk, step_pk):
    workflow = get_object_or_404(Workflow, pk=workflow_pk)
    step = get_object_or_404(WorkflowStep, pk=step_pk, workflow=workflow)
    user = request.user

    can_modify = (
        user.role == 'SUPER_ADMIN' or
        (user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == workflow.agency)
    )

    if request.method == 'GET':
        serializer = WorkflowStepSerializer(step)
        return Response(serializer.data)

    if not can_modify:
        return Response(
            {'detail': 'Not authorized to modify this workflow.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if workflow.status == 'PUBLISHED':
        return Response(
            {'detail': 'Cannot modify steps of a published workflow.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.method in ['PUT', 'PATCH']:
        serializer = WorkflowStepSerializer(step, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        step.delete()
        # Reorder remaining steps to maintain continuity
        remaining = workflow.steps.order_by('order', 'id')
        for idx, s in enumerate(remaining, start=1):
            if s.order != idx:
                s.order = idx
                s.save(update_fields=['order'])
        return Response({'detail': 'Step deleted and remaining steps reordered.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def step_reorder(request, workflow_pk):
    """
    Reorder steps by sending: {"step_orders": [{"id": 5, "order": 1}, {"id": 3, "order": 2}, ...]}
    """
    workflow = get_object_or_404(Workflow, pk=workflow_pk)
    user = request.user

    can_modify = (
        user.role == 'SUPER_ADMIN' or
        (user.role in ['AGENCY_ADMIN', 'DEVELOPER'] and user.agency == workflow.agency)
    )
    if not can_modify:
        return Response(
            {'detail': 'Not authorized to modify this workflow.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if workflow.status == 'PUBLISHED':
        return Response(
            {'detail': 'Cannot reorder steps of a published workflow.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    step_orders = request.data.get('step_orders', [])
    if not isinstance(step_orders, list):
        return Response(
            {'detail': 'step_orders must be a list of {id, order} objects.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    updated = []
    for item in step_orders:
        try:
            step = WorkflowStep.objects.get(pk=item['id'], workflow=workflow)
            step.order = item['order']
            step.save(update_fields=['order'])
            updated.append(step.id)
        except (WorkflowStep.DoesNotExist, KeyError, TypeError):
            continue

    # Return reordered steps
    steps = workflow.steps.order_by('order', 'id')
    serializer = WorkflowStepSerializer(steps, many=True)
    return Response({
        'detail': f'Reordered {len(updated)} steps.',
        'steps': serializer.data
    })