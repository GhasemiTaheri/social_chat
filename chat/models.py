import random
from django.contrib.auth.models import AbstractUser
from django.db import models


def code_generator():
    data = "abcdefghijklmnopqrstuvwxyz123456789"
    result = ""
    for _ in range(15):
        result += data[random.randint(0, (len(data) - 1))]
    return result


class User(AbstractUser):
    avatar = models.ImageField(upload_to='user_avatar/', blank=True, null=True)
    bio = models.TextField(max_length=200)


class Group(models.Model):
    name = models.CharField(max_length=50)
    unique_id = models.CharField(max_length=15, unique=True, default=code_generator)
    member = models.ManyToManyField(to=User, related_name="group_member")
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="group_creator")

    def member_count(self):
        return self.member.count()

    def __str__(self):
        return self.unique_id


class Message(models.Model):
    sender = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="message_sender")
    text = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)
    to_group = models.ForeignKey(to=Group, null=True, blank=True, on_delete=models.CASCADE,
                                 related_name="message_to_group")
    to_user = models.ForeignKey(to=User, null=True, blank=True, on_delete=models.CASCADE,
                                related_name="message_to_user")

    def letter_count(self):
        return len(self.text)

    def __str__(self):
        return self.text
