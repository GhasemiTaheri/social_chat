from django.urls import path
from rest_framework.routers import SimpleRouter

from chat.views import DashboardView, ConversationViewSet

router = SimpleRouter()
router.register('conversation', ConversationViewSet, basename='conversation')

app_name = "chat"
urlpatterns = [
                  path('', DashboardView.as_view(), name="dashboard")
              ] + router.urls
