from django.urls import path
from .views import *

app_name = "user"
urlpatterns = [
    path("password-reset/", password_reset_request, name="password_reset"),
    path("user-update/", UserUpdateView.as_view(), name="user_update"),
]
