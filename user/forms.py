from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from user.models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    username = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control form-control-lg my-1'}))
    email = forms.EmailField(required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg my-1'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg my-1'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg my-1'}))

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


class UpdateUserProfile(UserChangeForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'avatar', 'bio')

    first_name = forms.CharField(required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'John'}))
    last_name = forms.CharField(required=False,
                                widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Scott'}))
    email = forms.CharField(required=False,
                            widget=forms.EmailInput(
                                attrs={'class': 'form-control mb-3', 'placeholder': 'YourEmai@...'}))
    bio = forms.CharField(required=False,
                          widget=forms.Textarea(attrs={'class': 'form-control my-1', 'placeholder': 'Biography...'}))

    def clean_avatar(self):
        pic = self.cleaned_data.get("avatar")
        if pic:
            if pic.size > 1000000:
                raise forms.ValidationError("Image size is too large, please select another image")
        return pic
