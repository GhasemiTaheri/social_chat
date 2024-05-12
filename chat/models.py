from django.contrib.auth import get_user_model
from django.db import models


class Group:
    pass


class Conversation(models.Model):
    SINGLE = "si"
    GROUP = "gr"

    CONVERSATION_TYPES = [
        (SINGLE, "Single"),
        (GROUP, "Group")
    ]

    title = models.CharField(max_length=100)
    creator = models.ForeignKey(get_user_model(),
                                on_delete=models.SET_DEFAULT,
                                # 0 default value means deleted account
                                default=0)
    conversation_type = models.CharField(max_length=2, choices=CONVERSATION_TYPES, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
