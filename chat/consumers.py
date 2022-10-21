from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
import json
from channels.db import database_sync_to_async
from chat.models import Group, Message


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.user = self.scope['user']
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat = await self.get_chat()
        self.chat_room_id = f"chat_{self.chat_id}"

        if self.chat:
            await self.channel_layer.group_add(
                self.chat_room_id,
                self.channel_name)

            await self.send({
                'type': 'websocket.accept'
            })
        else:
            await self.send({
                'type': 'websocket.close'
            })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.chat_room_id,
            self.channel_name
        )
        raise StopConsumer()

    async def websocket_receive(self, event):
        text_data = event.get('text', None)

        if text_data:
            text_data_json = json.loads(text_data)
            text = text_data_json['text']

            msg = await self.create_message(text)
            if msg:
                await self.channel_layer.group_send(
                    self.chat_room_id,
                    {
                        'type': 'chat_message',
                        'message': msg,
                        'sender_channel_name': self.channel_name
                    }
                )

    async def chat_message(self, event):
        message = event['message']

        await self.send({
            'type': 'websocket.send',
            'text': message
        })

    @database_sync_to_async
    def get_chat(self):
        try:
            chat = Group.objects.get(unique_id=self.chat_id)
            return chat
        except Group.DoesNotExist:
            return None

    @database_sync_to_async
    def create_message(self, text):
        if self.chat.owner == self.user or self.chat.member.filter(id=self.user.id).exists():
            msg_obj = Message.objects.create(to_group_id=self.chat.id, sender_id=self.user.id, text=text)
            j = msg_obj.serializer()
            return json.dumps([j], default=str)
        return None
