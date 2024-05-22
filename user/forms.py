from django.contrib.auth.forms import UserCreationForm
from django import forms

from user.models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
