from asgiref.sync import async_to_sync
from django.conf import settings

from channels.layers import get_channel_layer as redis_channel_layer


class WebSocketMixin:
    channel_layers = redis_channel_layer()
    redis_server = settings.REDIS_SERVER

    def get_channel_layer(self):
        return self.channel_layers

    def get_redis_server(self):
        return self.redis_server

    def get_user_channel_layer(self, user_id):
        redis = self.get_redis_server()
        try:
            return redis.get(f'channel_user_{user_id}')
        except Exception as e:
            print(e)

    def user_send(self, user_id, payload):
        pass

    def group_send(self, group_id, payload):
        channel_layer = self.get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_id, payload)

    def add_users_to_group(self, group_id: str, users: list, *, payload: dict = None):
        channel_layer = self.get_channel_layer()

        for user in users:
            user_channel = self.get_user_channel_layer(user)
            if user_channel:
                async_to_sync(channel_layer.group_add)(group_id, user_channel)

        if payload:
            self.group_send(group_id, payload)

    def remove_from_group(self, group_id, users, *, payload: dict = None):
        channel_layer = self.get_channel_layer()

        for user in users:
            user_channel = self.get_user_channel_layer(user)
            if user_channel:
                async_to_sync(channel_layer.group_discard)(group_id, user_channel)

        if payload:
            self.group_send(group_id, payload)
