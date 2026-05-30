from rest_framework import serializers
from .models import Workflow, WorkflowStep
from apps.agencies.serializers import AgencySerializer
from apps.services.serializers import ServiceEndpointListSerializer

class WorkflowStepSerializer(serializers.ModelSerializer):
    service = ServiceEndpointListSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkflowStep._meta.get_field('service').related_model.objects.all(),
        source='service',
        write_only=True,
        required=False,
        allow_null=True
    )
    is_repeatable = serializers.BooleanField(required=False)
    min_repetitions = serializers.IntegerField(required=False)
    max_repetitions = serializers.IntegerField(required=False)

    class Meta:
        model = WorkflowStep
        fields = [
            'id', 'workflow', 'service', 'service_id', 'step_type', 'name',
            'order', 'conditions', 'timeout_seconds', 'retry_policy',
            'requires_approval', 'approver_roles', 'config',
            'is_repeatable', 'min_repetitions', 'max_repetitions',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
class WorkflowListSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    agency_code = serializers.CharField(source='agency.code', read_only=True)
    step_count = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'agency_name', 'agency_code',
            'status', 'version', 'is_published', 'step_count',
            'created_at', 'updated_at'
        ]

    def get_step_count(self, obj):
        return obj.steps.count()


class WorkflowDetailSerializer(serializers.ModelSerializer):
    agency = AgencySerializer(read_only=True)
    agency_id = serializers.PrimaryKeyRelatedField(
        queryset=Workflow._meta.get_field('agency').related_model.objects.all(),
        source='agency',
        write_only=True
    )
    steps = WorkflowStepSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'description', 'agency', 'agency_id',
            'status', 'version', 'is_published', 'steps',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'version', 'is_published', 'created_at', 'updated_at', 'created_by']


class WorkflowCreateSerializer(serializers.ModelSerializer):
    agency_id = serializers.PrimaryKeyRelatedField(
        queryset=Workflow._meta.get_field('agency').related_model.objects.all(),
        source='agency'
    )

    class Meta:
        model = Workflow
        fields = ['id', 'name', 'description', 'agency_id']
        read_only_fields = ['id']