from django.db import models
from django.db.models import Count, Q


class GroupConversationManager(models.Manager):

    def get_queryset(self):
        # just return group conversation
        from chat.models import Conversation
        return super().get_queryset().filter(conversation_type=Conversation.GROUP)

    def create(self, **kwargs):
        kwargs.update({'conversation_type': 'gr'})
        return super().create(**kwargs)


class PrivateConversationManager(models.Manager):
    def get_queryset(self):
        # just return private conversation
        from chat.models import Conversation
        return super().get_queryset().filter(conversation_type=Conversation.SINGLE)

    def create(self, **kwargs):
        kwargs.update({'conversation_type': 'si'})
        return super().create(**kwargs)

    def private_conversation_exists(self, user1, user2):
        q1 = self.filter(participant__user_id=user1.id).values_list('id', flat=True)
        queryset = (self.filter(id__in=q1)
                    .annotate(other_part=Count('participant', filter=Q(participant__user_id=user2.id)))
                    .filter(other_part__gt=0))
        return queryset
