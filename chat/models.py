import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import Coalesce

from chat.managers import GroupConversationManager, PrivateConversationManager


class Conversation(models.Model):
    SINGLE = "si"
    GROUP = "gr"

    CONVERSATION_TYPES = [
        (SINGLE, "Single"),
        (GROUP, "Group")
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    creator = models.ForeignKey(get_user_model(),
                                on_delete=models.SET_NULL,
                                # null value means deleted account
                                null=True)
    conversation_type = models.CharField(max_length=2, choices=CONVERSATION_TYPES, null=True)
    # only group can have avatar
    avatar = models.ImageField(upload_to='group_avatar/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def member_count(self):
        return self.participant_set.count()

    @property
    def last_message(self):
        return self.message_set.last()

    def unread_message_count(self, participant):
        """
        This method calculates the number of unread messages by a user
        """
        try:
            conv_user = self.participant_set.get(user=participant)
            return (self.message_set
                    .filter(create_at__gt=Coalesce(conv_user.last_read, conv_user.created_at))
                    .count())
        except:
            return 0

    def get_single_conversation_title(self, user):
        return self.participant_set.exclude(user=user).first().user.display_name

    def __str__(self):
        return f"{self.get_conversation_type_display()} - {self.title}"


class GroupConversation(Conversation):
    """
    This is a proxy model created for ease of access to group conversation.
    """
    objects = GroupConversationManager()

    class Meta:
        proxy = True

    def member_count(self):
        return self.participant_set.count()


class PrivateConversation(Conversation):
    """
    This is a proxy model created for ease of access to private conversation.
    """
    objects = PrivateConversationManager()

    class Meta:
        proxy = True

    def participants(self):
        return ', '.join(item.user.username for item in self.participant_set.all())


class Participant(models.Model):
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.SET_NULL,
                             # null value means deleted account
                             null=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    last_read = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "conversation")


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    text = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.display_name}: {self.text}"
