from rest_framework import serializers
from .models import ServiceEndpoint, ServiceField


class ServiceFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceField
        fields = [
            'id','service', 'name', 'label', 'field_type', 'required', 'location',
            'placeholder', 'help_text', 'default_value', 'validation_regex',
            'min_length', 'max_length', 'options', 'order', 'is_sensitive'
        ]


class AgencyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceEndpoint._meta.get_field('agency').related_model
        fields = ['id', 'name', 'code']


class ServiceEndpointSerializer(serializers.ModelSerializer):
    agency = AgencyBriefSerializer(read_only=True)
    agency_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceEndpoint._meta.get_field('agency').related_model.objects.all(),
        source='agency',
        write_only=True
    )
    full_url = serializers.CharField(source='get_full_url', read_only=True)
    service_fields = ServiceFieldSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceEndpoint
        fields = [
            'id', 'agency', 'agency_id', 'name', 'description',
            'endpoint_url', 'full_url', 'http_method', 'headers',
            'response_schema', 'field_definitions', 'service_fields',
            'authentication_override', 'timeout_seconds', 'retry_count',
            'status', 'health_status', 'version', 'rate_limits',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'health_status', 'created_at', 'updated_at', 'created_by']


class ServiceEndpointListSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    agency_code = serializers.CharField(source='agency.code', read_only=True)
    full_url = serializers.CharField(source='get_full_url', read_only=True)

    class Meta:
        model = ServiceEndpoint
        fields = [
            'id', 'name', 'agency_name', 'agency_code', 'full_url',
            'http_method', 'status', 'health_status', 'version', 'created_at'
        ]


class ServiceSchemaSerializer(serializers.Serializer):
    """Serializer for the auto-generated API contract"""
    service_id = serializers.IntegerField()
    service_name = serializers.CharField()
    description = serializers.CharField()
    http_method = serializers.CharField()
    endpoint_url = serializers.CharField()
    fields = serializers.ListField(child=serializers.DictField())


class ServicePreviewSerializer(serializers.Serializer):
    """Serializer for request preview"""
    raw_values = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        help_text="User-submitted values keyed by field name"
    )


class ServiceExecuteSerializer(serializers.Serializer):
    """Serializer for executing a service with raw values"""
    raw_values = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        help_text="User-submitted values keyed by field name"
    )