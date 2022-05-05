from django.contrib.auth.forms import UserCreationForm
from django import forms

from user.models import User


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control form-control-lg my-1'}))
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg my-1'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg my-1'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg my-1'}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        exists = None
        email = self.cleaned_data.get("email")
        try:
            exists = User.objects.filter(email=email)
        except:
            pass

        if exists:
            raise forms.ValidationError("A user with that username already exists.")
        else:
            return email
