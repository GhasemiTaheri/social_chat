from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(upload_to='user_avatar/', blank=True, null=True)
    bio = models.TextField(max_length=200, null=True, blank=True)
    last_online = models.DateTimeField(null=True)
