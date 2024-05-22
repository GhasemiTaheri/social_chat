from django.urls import path

from user.views import PasswordResetView, SignUpView, UserUpdateDestroyApiView

app_name = "user"
urlpatterns = [
    path('sing-up/', SignUpView.as_view(), name="register"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("user-update/", UserUpdateDestroyApiView.as_view(), name="user_update"),
]
