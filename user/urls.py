from django.urls import path
from rest_framework.routers import DefaultRouter

from user.views import PasswordResetView, SignUpView, UserUpdateDestroyApiView, UserReadViewSet

router = DefaultRouter()
router.register('user', UserReadViewSet, basename='user')

app_name = "user"
urlpatterns = [
                  path('sing-up/', SignUpView.as_view(), name="register"),
                  path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
                  path("user-update/", UserUpdateDestroyApiView.as_view(), name="user_update"),
              ] + router.urls
