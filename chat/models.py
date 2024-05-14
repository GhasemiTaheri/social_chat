import uuid

from django.contrib.auth import get_user_model
from django.db import models

from chat.managers import GroupConversationManager, PrivateConversationManager


class Group:
    pass


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
                                on_delete=models.SET_DEFAULT,
                                # 0 default value means deleted account
                                default=0)
    conversation_type = models.CharField(max_length=2, choices=CONVERSATION_TYPES, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        return ', '.join(user.username for user in self.participant_set.all())


class Participant(models.Model):
    user = models.ForeignKey(get_user_model(),
                             on_delete=models.SET_DEFAULT,
                             # 0 default value means deleted account
                             default=0)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    last_read = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    text = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
