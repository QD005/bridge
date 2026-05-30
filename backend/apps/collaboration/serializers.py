from rest_framework import serializers
from .models import Conversation, Message
from apps.accounts.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    is_read_by_me = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'content', 'message_type',
            'assigned_to', 'task_status', 'task_due_date',
            'mentions', 'attachments', 'priority', 'is_edited',
            'is_pinned',
            'read_by', 'read_count', 'is_read_by_me',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'sender', 'read_count']

    def get_is_read_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return request.user.id in obj.read_by
        return False


class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Conversation
        fields = [
            'id', 'workflow', 'execution', 'agency',
            'conversation_type', 'title', 'is_active',
            'participants', 'participant_ids', 'created_by',
            'last_message', 'message_count', 'unread_count',
            'created_at', 'updated_at'
        ]

    def get_last_message(self, obj):
        last = obj.messages.order_by('-created_at').first()
        return MessageSerializer(last, context=self.context).data if last else None

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            user_id = request.user.id
            # SQLite-compatible: count in Python since JSONField __contains isn't supported on SQLite
            count = 0
            for msg in obj.messages.only('read_by').all():
                if user_id not in (msg.read_by or []):
                    count += 1
            return count
        return 0

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = super().create(validated_data)
        if participant_ids:
            conversation.participants.set(participant_ids)
        return conversation


class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id', 'workflow', 'execution', 'agency',
            'conversation_type', 'title', 'is_active',
            'participants', 'messages', 'created_by',
            'created_at', 'updated_at'
        ]