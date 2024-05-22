from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.functional import cached_property


class User(AbstractUser):
    avatar = models.ImageField(upload_to='user_avatar/', blank=True, null=True)
    last_online = models.DateTimeField(null=True)

    @cached_property
    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        else:
            return self.avatar.storage.url('defaults/user_default.jpg')
