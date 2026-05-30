from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ['sender', 'content', 'message_type', 'priority', 'created_at']
    readonly_fields = ['created_at']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'conversation_type', 'agency', 'is_active', 'created_by', 'updated_at']
    list_filter = ['conversation_type', 'is_active', 'created_at']
    search_fields = ['title', 'id']
    filter_horizontal = ['participants']
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'sender', 'message_type', 'task_status', 'priority', 'created_at']
    list_filter = ['message_type', 'priority', 'task_status', 'created_at']
    search_fields = ['content']