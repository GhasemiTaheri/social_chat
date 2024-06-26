from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.db.models import CharField
from django.db.models.functions import Cast
from django.utils import timezone

from chat.models import Message, Conversation, Participant
from chat.serializers import ReceiveMessageSerializer, SendMessageSerializer
from django.conf import settings


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def websocket_connect(self, message):
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            return await self.close()

        await self.set_conversations()

        settings.REDIS_SERVER.set(f"channel_user_{self.user.id}", str(self.channel_name))

        return await super().websocket_connect(message)

    async def disconnect(self, code):
        settings.REDIS_SERVER.delete(f"channel_user_{self.user.id}")

        self.user.last_online = timezone.now()
        await self.user.asave()

        return await super().disconnect(code)

    async def receive_json(self, content, **kwargs):
        try:
            serializer = ReceiveMessageSerializer(data=content, context={'request': self.scope})
            serializer.is_valid(raise_exception=True)
        except:
            return await self.send(text_data='Invalid request')

        msg = await Message.objects.acreate(sender_id=self.user.id,
                                            conversation_id=serializer.validated_data.get('conversation'),
                                            text=serializer.validated_data.get('message'))
        await database_sync_to_async(lambda: (Participant.objects
                                              .filter(user_id=msg.sender.id,
                                                      conversation_id=msg.conversation.id)
                                              .update(last_read=timezone.now())))()
        if msg:
            await self.channel_layer.group_send(
                str(serializer.validated_data.get('conversation')),
                {
                    'type': 'new.message',
                    'message': await database_sync_to_async(lambda: ({
                        'event_type': 'new_message',
                        'data': SendMessageSerializer(instance=msg).data
                    }))()
                }
            )

    async def new_message(self, event):
        await self.send_json(event.get('message'))

    @database_sync_to_async
    def set_conversations(self) -> None:
        try:
            conversations = (Conversation.objects.filter(participant__user=self.user)
                             .annotate(str_id=Cast('id', CharField()))
                             .values_list('str_id', flat=True))
            self.groups.extend(list(conversations))
        except Exception as e:
            print(e)
            raise StopConsumer()
