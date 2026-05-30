from rest_framework import serializers
from .models import AuditLog
from apps.accounts.serializers import UserSerializer

class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'action', 'status', 'entity_type', 'entity_id',
            'entity_name', 'http_method', 'url', 'ip_address',
            'previous_data', 'new_data', 'error_message', 'status_code',
            'description', 'created_at'
        ]


class AuditLogListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user_name', 'user_role', 'action', 'status',
            'entity_type', 'entity_name', 'http_method', 'status_code',
            'description', 'created_at'
        ]