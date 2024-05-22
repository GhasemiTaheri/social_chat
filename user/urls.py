from django.urls import path

from user.views import PasswordResetView, SignUpView, UserUpdateApiView

app_name = "user"
urlpatterns = [
    path('sing-up/', SignUpView.as_view(), name="register"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("user-update/", UserUpdateApiView.as_view(), name="user_update"),
]
