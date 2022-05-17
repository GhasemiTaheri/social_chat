from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    avatar = models.ImageField(upload_to='user_avatar/', blank=True, null=True)
    bio = models.TextField(max_length=200, null=True, blank=True)

    def serializer(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "avatar": self.avatar.name,
            "bio": self.bio
        }
