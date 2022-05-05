from django.contrib import admin

# Register your models here.
from chat.models import User

admin.site.register(User)