from django.db import models


class GroupConversationManager(models.Manager):

    def get_queryset(self):
        # just return group conversation
        from chat.models import Conversation
        return super().get_queryset().filter(conversation_type=Conversation.GROUP)


class PrivateConversationManager(models.Manager):
    def get_queryset(self):
        # just return private conversation
        from chat.models import Conversation
        return super().get_queryset().filter(conversation_type=Conversation.SINGLE)
