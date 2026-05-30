import json
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import Conversation, Message
from .serializers import MessageSerializer

User = get_user_model()

# Module-level presence tracker
ROOM_PRESENCE = {}


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        query_string = self.scope['query_string'].decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]
        
        self.user = await self.get_user_from_token(token)
        
        if not self.user:
            await self.close(code=4001)
            return
        
        can_access = await self.can_access_conversation(self.user, self.conversation_id)
        if not can_access:
            await self.close(code=4003)
            return
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        if self.room_group_name not in ROOM_PRESENCE:
            ROOM_PRESENCE[self.room_group_name] = {}
        
        ROOM_PRESENCE[self.room_group_name][self.user.id] = {
            'user_id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'presence_update',
                'users': list(ROOM_PRESENCE[self.room_group_name].values())
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name') and hasattr(self, 'user'):
            if self.room_group_name in ROOM_PRESENCE:
                ROOM_PRESENCE[self.room_group_name].pop(self.user.id, None)
                if not ROOM_PRESENCE[self.room_group_name]:
                    del ROOM_PRESENCE[self.room_group_name]
                else:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'presence_update',
                            'users': list(ROOM_PRESENCE[self.room_group_name].values())
                        }
                    )
            
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            action = data.get('action', 'message')
            
            if action == 'message':
                await self.handle_message(data)
            elif action == 'typing':
                await self.handle_typing(data)
            elif action == 'read':
                await self.handle_read(data)
            elif action == 'task_update':
                await self.handle_task_update(data)
            elif action == 'pin':
                await self.handle_pin(data)
            elif action == 'get_presence':
                await self.handle_get_presence()
                
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'detail': str(e)
            }))

    async def handle_message(self, data):
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'TEXT')
        assigned_to_id = data.get('assigned_to')
        attachments = data.get('attachments', [])
        priority = data.get('priority', 'NORMAL')
        
        if not content and not attachments:
            return
        
        message = await self.create_message(
            content=content,
            message_type=message_type,
            assigned_to_id=assigned_to_id,
            attachments=attachments,
            priority=priority
        )
        
        # CRITICAL: Serialize in sync context
        msg_data = await self.serialize_message(message)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg_data
            }
        )
        
        await self.update_conversation_timestamp()

    async def handle_typing(self, data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'user_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.email,
                'is_typing': data.get('is_typing', False)
            }
        )

    async def handle_read(self, data):
        message_id = data.get('message_id')
        await self.mark_message_read(message_id, self.user.id)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'read_receipt',
                'message_id': message_id,
                'user_id': self.user.id,
            }
        )

    async def handle_task_update(self, data):
        message_id = data.get('message_id')
        new_status = data.get('task_status')
        message = await self.update_task_status(message_id, new_status)
        if message:
            msg_data = await self.serialize_message(message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'task_updated',
                    'message': msg_data
                }
            )

    async def handle_pin(self, data):
        message_id = data.get('message_id')
        message = await self.toggle_pin(message_id)
        if message:
            msg_data = await self.serialize_message(message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_pinned',
                    'message': msg_data
                }
            )

    async def handle_get_presence(self):
        users = []
        if self.room_group_name in ROOM_PRESENCE:
            users = list(ROOM_PRESENCE[self.room_group_name].values())
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'users': users
        }))

    # --- Group message handlers ---
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'data': event['message']
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'data': event
        }))

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read',
            'data': event
        }))

    async def task_updated(self, event):
        await self.send(text_data=json.dumps({
            'type': 'task_updated',
            'data': event['message']
        }))

    async def message_pinned(self, event):
        await self.send(text_data=json.dumps({
            'type': 'pin',
            'data': event['message']
        }))

    async def presence_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'presence',
            'users': event['users']
        }))

    # --- CRITICAL FIX: Wrap serializer in sync_to_async ---
    
    @sync_to_async
    def serialize_message(self, msg):
        return MessageSerializer(msg).data

    # --- Database helpers ---

    @database_sync_to_async
    def get_user_from_token(self, token):
        if not token:
            return None
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (TokenError, User.DoesNotExist):
            return None

    @database_sync_to_async
    def can_access_conversation(self, user, conversation_id):
        try:
            conv = Conversation.objects.get(id=conversation_id)
            if user.role in ['SUPER_ADMIN', 'AUDITOR']:
                return True
            if conv.participants.filter(id=user.id).exists():
                return True
            if conv.created_by == user:
                return True
            if conv.agency and conv.agency == user.agency:
                return True
            if conv.workflow and conv.workflow.agency == user.agency:
                return True
            if conv.execution and conv.execution.workflow.agency == user.agency:
                return True
            return False
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def create_message(self, content, message_type, assigned_to_id, attachments, priority):
        msg = Message.objects.create(
            conversation_id=self.conversation_id,
            sender=self.user,
            content=content,
            message_type=message_type,
            assigned_to_id=assigned_to_id if assigned_to_id else None,
            attachments=attachments,
            priority=priority
        )
        return msg

    @database_sync_to_async
    def update_conversation_timestamp(self):
        from django.db import models
        Conversation.objects.filter(id=self.conversation_id).update(updated_at=models.functions.Now())

    @database_sync_to_async
    def mark_message_read(self, message_id, user_id):
        try:
            msg = Message.objects.get(id=message_id, conversation_id=self.conversation_id)
            if user_id not in (msg.read_by or []):
                msg.read_by.append(user_id)
                msg.save(update_fields=['read_by'])
        except Message.DoesNotExist:
            pass

    @database_sync_to_async
    def update_task_status(self, message_id, new_status):
        try:
            msg = Message.objects.select_related('sender', 'assigned_to').get(
                id=message_id, conversation_id=self.conversation_id, message_type='TASK'
            )
            msg.task_status = new_status
            msg.save(update_fields=['task_status'])
            return msg
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def toggle_pin(self, message_id):
        try:
            msg = Message.objects.select_related('sender', 'assigned_to').get(
                id=message_id, conversation_id=self.conversation_id
            )
            msg.is_pinned = not msg.is_pinned
            msg.save(update_fields=['is_pinned'])
            return msg
        except Message.DoesNotExist:
            return None