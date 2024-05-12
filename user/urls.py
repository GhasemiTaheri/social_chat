from django.urls import path

from user.views import PasswordResetView, UserUpdateView, SignUpView

app_name = "user"
urlpatterns = [
    path('sing-up/', SignUpView.as_view(), name="register"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("user-update/", UserUpdateView.as_view(), name="user_update"),
]
