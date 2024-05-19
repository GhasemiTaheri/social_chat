from django.urls import path
from rest_framework.routers import SimpleRouter

from chat.views import DashboardView, GroupCreateView, ConversationViewSet

router = SimpleRouter()
router.register('conversation', ConversationViewSet, basename='conversation')

app_name = "chat"
urlpatterns = [
                  path('', DashboardView.as_view(), name="dashboard"),
                  path('new-group/', GroupCreateView.as_view(), name="new_group"),
              ] + router.urls
