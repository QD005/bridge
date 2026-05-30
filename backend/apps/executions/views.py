import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import WorkflowExecution, ExecutionStep, StepSubmission
from .serializers import (
    WorkflowExecutionListSerializer,
    WorkflowExecutionDetailSerializer,
    StartExecutionSerializer,
    ExecutionStepSerializer,
    StepSubmissionSerializer
)
from .tasks import execute_service_step, evaluate_condition


def notify_execution_update(execution):
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"execution_{execution.id}",
            {
                "type": "execution_update",
                "data": {
                    "id": execution.id,
                    "status": execution.status,
                    "updated_at": str(execution.updated_at),
                }
            }
        )
    except Exception:
        pass


def get_execution_queryset(user):
    if user.role == 'SUPER_ADMIN':
        return WorkflowExecution.objects.all().select_related('workflow__agency', 'initiated_by').prefetch_related('steps__submissions')
    elif user.role == 'AUDITOR':
        return WorkflowExecution.objects.all().select_related('workflow__agency', 'initiated_by').prefetch_related('steps__submissions')
    elif user.role in ['AGENCY_ADMIN', 'DEVELOPER', 'OPERATIONS_OFFICER']:
        q = Q(workflow__agency=user.agency) | Q(initiated_by=user)
        return WorkflowExecution.objects.filter(q).select_related('workflow__agency', 'initiated_by').prefetch_related('steps__submissions')
    return WorkflowExecution.objects.none()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def execution_list_create(request):
    user = request.user

    if request.method == 'GET':
        queryset = WorkflowExecution.objects.select_related('workflow__agency', 'initiated_by').prefetch_related('steps__submissions', 'steps__workflow_step__service')
        workflow_id = request.query_params.get('workflow')
        status_filter = request.query_params.get('status')
        agency_id = request.query_params.get('agency')
        search = request.query_params.get('search')

        if workflow_id:
            queryset = queryset.filter(workflow_id=workflow_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        if agency_id:
            queryset = queryset.filter(workflow__agency_id=agency_id)
        if search:
            queryset = queryset.filter(
                Q(applicant_name__icontains=search) | 
                Q(workflow__name__icontains=search) |
                Q(payload__icontains=search)
            )

        # Permission filter
        if user.role not in ['SUPER_ADMIN', 'AUDITOR']:
            queryset = queryset.filter(
                Q(workflow__agency=user.agency) | Q(initiated_by=user)
            )

        serializer = WorkflowExecutionListSerializer(queryset, many=True)
        return Response(serializer.data)

    # POST — Create a new Request/Case
    serializer = StartExecutionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    workflow_id = serializer.validated_data['workflow_id']
    payload = serializer.validated_data.get('payload', {})
    applicant_name = serializer.validated_data.get('applicant_name', '')
    applicant_contact = serializer.validated_data.get('applicant_contact', '')

    from apps.workflows.models import Workflow
    workflow = get_object_or_404(Workflow, pk=workflow_id)

    if workflow.status != 'PUBLISHED':
        return Response(
            {'detail': 'Cannot use a workflow that is not published.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if user.role != 'SUPER_ADMIN' and user.agency != workflow.agency:
        return Response(
            {'detail': 'You can only create requests for workflows from your own agency.'},
            status=status.HTTP_403_FORBIDDEN
        )

    with transaction.atomic():
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            initiated_by=user,
            applicant_name=applicant_name,
            applicant_contact=applicant_contact,
            payload=payload,
            status='PENDING'
        )

        # Create all execution steps upfront
        for step in workflow.steps.order_by('order'):
            ExecutionStep.objects.create(
                workflow_execution=execution,
                workflow_step=step,
                order=step.order,
                status='PENDING'
            )

    return Response(
        WorkflowExecutionListSerializer(execution).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def execution_detail(request, pk):
    execution = get_object_or_404(
        WorkflowExecution.objects.select_related('workflow__agency', 'initiated_by').prefetch_related(
            'steps__submissions__submitted_by',
            'steps__workflow_step__service__agency',
            'steps__approved_by'
        ),
        pk=pk
    )
    user = request.user

    if user.role not in ['SUPER_ADMIN', 'AUDITOR']:
        if execution.initiated_by != user and execution.workflow.agency != user.agency:
            return Response(
                {'detail': 'Not authorized to view this request.'},
                status=status.HTTP_403_FORBIDDEN
            )

    serializer = WorkflowExecutionDetailSerializer(execution)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execution_cancel(request, pk):
    execution = get_object_or_404(WorkflowExecution, pk=pk)
    user = request.user

    if user.role != 'SUPER_ADMIN' and execution.initiated_by != user and execution.workflow.agency != user.agency:
        return Response(
            {'detail': 'Not authorized to cancel this request.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if execution.status in ['COMPLETED', 'REJECTED', 'CANCELLED']:
        return Response(
            {'detail': f'Request is already {execution.status.lower()}.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    execution.status = 'CANCELLED'
    execution.completed_at = timezone.now()
    execution.save(update_fields=['status', 'completed_at'])
    execution.steps.filter(status__in=['PENDING', 'IN_PROGRESS']).update(status='CANCELLED')

    return Response({
        'detail': 'Request cancelled.',
        'execution': WorkflowExecutionListSerializer(execution).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execution_step_submit(request, pk, step_pk):
    """
    Submit data for a workflow step. Creates a new StepSubmission.
    Can be called multiple times for repeatable steps.
    Body: {"payload": {"nin": "CM123...", "tin": "100012..."}}
    """
    execution = get_object_or_404(WorkflowExecution, pk=pk)
    exec_step = get_object_or_404(ExecutionStep, pk=step_pk, workflow_execution=execution)
    user = request.user

    # Permission
    if user.role != 'SUPER_ADMIN' and user.agency != execution.workflow.agency:
        return Response(
            {'detail': 'Not authorized to submit for this request.'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check if step is already completed
    if exec_step.status == 'COMPLETED':
        return Response(
            {'detail': 'This step is already completed.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check sequential constraint
    if execution.workflow.is_sequential:
        previous_steps = execution.steps.filter(order__lt=exec_step.order)
        if previous_steps.exclude(status='COMPLETED').exists():
            return Response(
                {'detail': 'Previous steps must be completed first.'},
                status=status.HTTP_400_BAD_REQUEST
            )


    # Only block if there's already a SUCCESSFUL submission on a non-repeatable step
    successful_count = exec_step.submissions.filter(status='SUCCESS').count()
    if not exec_step.workflow_step.is_repeatable and successful_count >= 1:
        return Response(
            {'detail': 'This step has already been completed successfully.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get payload from request
    test_payload = request.data.get('payload', {})

    # Create submission record
    submission = StepSubmission.objects.create(
        execution_step=exec_step,
        submission_data=test_payload,
        status='PENDING',
        submitted_by=user
    )

    # Update step status
    exec_step.status = 'IN_PROGRESS'
    exec_step.save(update_fields=['status'])

    # Update execution status
    if execution.status == 'PENDING':
        execution.status = 'IN_PROGRESS'
        execution.save(update_fields=['status'])


    # Add this before the try block in execution_step_submit:

    # Validate against field_definitions if available
    service = exec_step.workflow_step.service
    if service and service.field_definitions:
        for field_def in service.field_definitions:
            field_name = field_def.get('name')
            field_value = test_payload.get(field_name)
            
            # Check required
            if field_def.get('required') and not field_value:
                return Response(
                    {'detail': f'Field "{field_def.get("label", field_name)}" is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check regex
            if field_def.get('validation_regex') and field_value:
                import re
                if not re.match(field_def['validation_regex'], str(field_value)):
                    return Response(
                        {'detail': f'Field "{field_def.get("label", field_name)}" format is invalid.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Check min/max length
            if field_def.get('min_length') and field_value:
                if len(str(field_value)) < field_def['min_length']:
                    return Response(
                        {'detail': f'Field "{field_def.get("label", field_name)}" must be at least {field_def["min_length"]} characters.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            if field_def.get('max_length') and field_value:
                if len(str(field_value)) > field_def['max_length']:
                    return Response(
                        {'detail': f'Field "{field_def.get("label", field_name)}" must be at most {field_def["max_length"]} characters.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

    # Execute the service call
    try:
        if exec_step.workflow_step.step_type == 'SERVICE' and exec_step.workflow_step.service:
            result = execute_service_step(exec_step.workflow_step.service, test_payload)
            submission.response_data = result
            submission.response_status_code = 200
            submission.status = 'SUCCESS'
            submission.save(update_fields=['response_data', 'response_status_code', 'status'])

        elif exec_step.workflow_step.step_type == 'CONDITIONAL':
            passed = evaluate_condition(exec_step.workflow_step, {'payload': execution.payload})
            submission.response_data = {'condition_passed': passed}
            submission.status = 'SUCCESS'
            submission.save(update_fields=['response_data', 'status'])

        elif exec_step.workflow_step.step_type in ['NOTIFICATION', 'DELAY']:
            submission.response_data = {'processed': True}
            submission.status = 'SUCCESS'
            submission.save(update_fields=['response_data', 'status'])

        else:
            # MANUAL_REVIEW, APPROVAL - just record the submission
            submission.status = 'SUCCESS'
            submission.save(update_fields=['status'])

        notify_execution_update(execution)

        return Response({
            'detail': 'Submission processed successfully.',
            'submission': StepSubmissionSerializer(submission).data,
            'step': ExecutionStepSerializer(exec_step).data
        })

    except Exception as e:
        submission.status = 'FAILED'
        submission.error_message = str(e)
        submission.save(update_fields=['status', 'error_message'])

        # CRITICAL FIX: Reset non-repeatable steps to PENDING so officer can retry
        if not exec_step.workflow_step.is_repeatable:
            exec_step.status = 'PENDING'
            exec_step.save(update_fields=['status'])

        return Response({
            'detail': f'Submission failed: {str(e)}',
            'submission': StepSubmissionSerializer(submission).data
        }, status=status.HTTP_502_BAD_GATEWAY)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execution_step_complete(request, pk, step_pk):
    """
    Mark a step as completed by the officer.
    This is done AFTER reviewing submissions and responses.
    Body: {"notes": "All directors verified successfully"}
    """
    execution = get_object_or_404(WorkflowExecution, pk=pk)
    exec_step = get_object_or_404(ExecutionStep, pk=step_pk, workflow_execution=execution)
    user = request.user

    if user.role != 'SUPER_ADMIN' and user.agency != execution.workflow.agency:
        return Response(
            {'detail': 'Not authorized.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if exec_step.status == 'COMPLETED':
        return Response(
            {'detail': 'Step is already completed.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    notes = request.data.get('notes', '')

    exec_step.status = 'COMPLETED'
    exec_step.officer_notes = notes
    exec_step.approved_by = user
    exec_step.approved_at = timezone.now()
    exec_step.save(update_fields=['status', 'officer_notes', 'approved_by', 'approved_at'])

    # Check if all steps are completed
    all_steps = execution.steps.all()
    if all(s.status == 'COMPLETED' for s in all_steps):
        execution.status = 'COMPLETED'
        execution.completed_at = timezone.now()
        execution.save(update_fields=['status', 'completed_at'])

    notify_execution_update(execution)

    return Response({
        'detail': 'Step marked as completed.',
        'step': ExecutionStepSerializer(exec_step).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execution_complete(request, pk):
    """
    Final completion of the entire request - issue certificate.
    """
    execution = get_object_or_404(WorkflowExecution, pk=pk)
    user = request.user

    if user.role != 'SUPER_ADMIN' and user.agency != execution.workflow.agency:
        return Response(
            {'detail': 'Not authorized.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if execution.status in ['COMPLETED', 'REJECTED', 'CANCELLED']:
        return Response(
            {'detail': f'Request is already {execution.status.lower()}.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if all steps are completed
    if not execution.steps.filter(status='COMPLETED').count() == execution.steps.count():
        return Response(
            {'detail': 'All steps must be completed before final approval.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    execution.status = 'COMPLETED'
    execution.completed_at = timezone.now()
    execution.result = {
        'completed_at': timezone.now().isoformat(),
        'approved_by': user.get_full_name(),
        'certificate_issued': True
    }
    execution.save(update_fields=['status', 'completed_at', 'result'])

    return Response({
        'detail': 'Request completed. Certificate issued.',
        'execution': WorkflowExecutionListSerializer(execution).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execution_reject(request, pk):
    execution = get_object_or_404(WorkflowExecution, pk=pk)
    user = request.user

    if user.role != 'SUPER_ADMIN' and user.agency != execution.workflow.agency:
        return Response(
            {'detail': 'Not authorized.'},
            status=status.HTTP_403_FORBIDDEN
        )

    reason = request.data.get('reason', '')
    execution.status = 'REJECTED'
    execution.completed_at = timezone.now()
    execution.result = {'rejected': True, 'reason': reason}
    execution.save(update_fields=['status', 'completed_at', 'result'])

    return Response({
        'detail': f'Request rejected. Reason: {reason}',
        'execution': WorkflowExecutionListSerializer(execution).data
    })