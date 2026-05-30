from rest_framework import serializers
from .models import WorkflowExecution, ExecutionStep, StepSubmission
from apps.workflows.serializers import WorkflowListSerializer
from apps.accounts.serializers import UserSerializer

class StepSubmissionSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)

    class Meta:
        model = StepSubmission
        fields = [
            'id', 'execution_step', 'submission_data', 'response_data',
            'response_status_code', 'status', 'error_message',
            'submitted_by', 'submitted_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ExecutionStepSerializer(serializers.ModelSerializer):
    step_name = serializers.CharField(source='workflow_step.name', read_only=True)
    step_type = serializers.CharField(source='workflow_step.step_type', read_only=True)
    is_repeatable = serializers.BooleanField(source='workflow_step.is_repeatable', read_only=True)
    max_repetitions = serializers.IntegerField(source='workflow_step.max_repetitions', read_only=True)
    service_name = serializers.CharField(source='workflow_step.service.name', read_only=True)
    service = serializers.SerializerMethodField()
    submissions = StepSubmissionSerializer(many=True, read_only=True)
    approver = UserSerializer(source='approved_by', read_only=True)
    submission_count = serializers.SerializerMethodField()

    class Meta:
        model = ExecutionStep
        fields = [
            'id', 'workflow_execution', 'workflow_step', 'step_name', 'step_type',
            'order', 'status', 'is_repeatable', 'max_repetitions',
            'service_name', 'service', 'submissions', 'submission_count',
            'officer_notes', 'approver', 'approved_at',
            'created_at', 'updated_at'
        ]

    def get_service(self, obj):
        if obj.workflow_step.service:
            from apps.services.serializers import ServiceEndpointListSerializer
            return ServiceEndpointListSerializer(obj.workflow_step.service).data
        return None

    def get_submission_count(self, obj):
        return obj.submissions.count()


class WorkflowExecutionListSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    agency_name = serializers.CharField(source='workflow.agency.name', read_only=True)
    initiated_by_name = serializers.CharField(source='initiated_by.get_full_name', read_only=True)
    completed_steps = serializers.SerializerMethodField()
    total_steps = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'workflow_name', 'agency_name',
            'applicant_name', 'applicant_contact',
            'status', 'started_at', 'completed_at',
            'initiated_by', 'initiated_by_name',
            'completed_steps', 'total_steps',
            'updated_at'
        ]

    def get_completed_steps(self, obj):
        return obj.steps.filter(status='COMPLETED').count()

    def get_total_steps(self, obj):
        return obj.steps.count()


class WorkflowExecutionDetailSerializer(serializers.ModelSerializer):
    workflow = WorkflowListSerializer(read_only=True)
    initiated_by = UserSerializer(read_only=True)
    steps = ExecutionStepSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'status', 'started_at', 'completed_at',
            'applicant_name', 'applicant_contact',
            'initiated_by', 'payload', 'result', 'error_message',
            'steps', 'updated_at'
        ]


class StartExecutionSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    applicant_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    applicant_contact = serializers.CharField(max_length=255, required=False, allow_blank=True)
    payload = serializers.JSONField(default=dict)