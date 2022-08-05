from django.urls import path
from .views import *

app_name = "chat"
urlpatterns = [
    path('', dashboard, name="dashboard"),
    path('create_group', create_group, name="create_group"),
    path('get_all_chat', get_all_chat, name="get_all_chat"),
    path('get_chat_message/<str:chat_id>', get_chat_message, name="get_chat_message"),
]
