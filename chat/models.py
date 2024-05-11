from django.contrib.auth import get_user_model
from django.db import models


class Group:
    pass


class Conversation(models.Model):
    title = models.CharField(max_length=100)
    creator = models.ForeignKey(get_user_model(), on_delete=models.SET_DEFAULT, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


class Participant(models.Model):
    SINGLE = "si"
    GROUP = "gr"

    CHAT_TYPES = [
        (SINGLE, "Single"),
        (GROUP, "Group")
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.SET_DEFAULT, default=0)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    chat_type = models.CharField(max_length=2, choices=CHAT_TYPES)
    added_at = models.DateTimeField(auto_now_add=True)
    last_read = models.DateTimeField(null=True, blank=True)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    text = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
