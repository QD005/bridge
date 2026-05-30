import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ExecutionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.execution_id = self.scope['url_route']['kwargs']['execution_id']
        self.group_name = f"execution_{self.execution_id}"

        # Join group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send immediate confirmation
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "execution_id": self.execution_id,
            "message": "Connected to execution updates."
        }))

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Handle any messages from client (optional)
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({
            "type": "echo",
            "received": data
        }))

    async def execution_update(self, event):
        """Handler for messages sent to the group"""
        await self.send(text_data=json.dumps(event['data']))