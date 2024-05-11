from django.urls import path

from chat.views import DashboardView

app_name = "chat"
urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard"),
]
