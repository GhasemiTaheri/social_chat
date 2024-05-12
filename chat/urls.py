from django.urls import path

from chat.views import DashboardView, GroupCreateView

app_name = "chat"
urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard"),
    path('new-group/', GroupCreateView.as_view(), name="new_group"),
]
