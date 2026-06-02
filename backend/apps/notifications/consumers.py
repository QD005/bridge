import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        # Reject anonymous
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.user_group = f"user_{self.user.id}"
        
        # Join user-specific group
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial unread count
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': count
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(
                self.user_group,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle client messages (e.g. ping, mark read)"""
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'mark_read':
            notif_id = data.get('notification_id')
            await self.mark_notification_read(notif_id)
            await self.send_unread_count()
        
        elif action == 'mark_all_read':
            await self.mark_all_read()
            await self.send_unread_count()

    async def notification_push(self, event):
        """Handle notification pushed from utils.py"""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'data': event['data']
        }))
        
        # Also update unread count
        await self.send_unread_count()

    async def send_unread_count(self):
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': count
        }))

    @database_sync_to_async
    def get_unread_count(self):
        from .models import Notification
        return Notification.objects.filter(user=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_notification_read(self, notif_id):
        from .models import Notification
        try:
            notif = Notification.objects.get(id=notif_id, user=self.user)
            notif.mark_read()
        except Notification.DoesNotExist:
            pass

    @database_sync_to_async
    def mark_all_read(self):
        from .models import Notification
        Notification.objects.mark_all_read(self.user)