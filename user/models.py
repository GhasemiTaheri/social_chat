from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property


class User(AbstractUser):
    avatar = models.ImageField(upload_to='user_avatar/', blank=True, null=True)
    last_online = models.DateTimeField(null=True)

    @property
    def display_name(self):
        if self.get_full_name():
            return self.get_full_name()
        else:
            return self.username

    @cached_property
    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        else:
            return self.avatar.storage.url('defaults/user_default.jpg')

    @cached_property
    def get_statics(self):
        """
        This property extracts user information to be used in the template.
        """
        from chat.models import Participant
        user_conversations = self.participant_set.values('conversation_id')
        result = {
            'message_count': self.message_set.count(),
            'conversation_count': user_conversations.count(),
            'friends_count': Participant.objects.filter(Q(conversation_id__in=user_conversations)
                                                        & ~Q(user_id=self.id)).count()
        }

        return result
