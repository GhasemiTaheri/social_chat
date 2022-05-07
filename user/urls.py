from django.urls import path
from .views import *

app_name = "user"
urlpatterns = [
    path('', index, name="index"),
    path("password_reset", password_reset_request, name="password_reset")
]
