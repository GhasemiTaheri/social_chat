from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from user.models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    # TODO: optimize clean_email func
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

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    bio = forms.CharField(required=False, widget=forms.Textarea())

    def clean_avatar(self):
        pic = self.cleaned_data.get("avatar")
        if pic:
            if pic.size > 1000000:
                raise forms.ValidationError("Image size is too large, please select another image")
        return pic
