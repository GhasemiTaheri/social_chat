from django.urls import path
from .views import *

app_name = "user"
urlpatterns = [
    path("password_reset/", password_reset_request, name="password_reset"),
    path("user_update/", user_update, name="user_update"),
]
