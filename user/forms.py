from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.urls import reverse

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
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    bio = forms.CharField(required=False, widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get("password")
        if password:
            password.help_text = """
            Raw passwords are not stored, so there is no way to see this
            user’s password, but you can change the password using
            <a href="{}">this form</a>.
            """.format(reverse('user:password_reset'))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'avatar', 'bio')

    def clean_avatar(self):
        pic = self.cleaned_data.get("avatar")
        if pic:
            if pic.size > 1000000:
                raise forms.ValidationError("Image size is too large, please select another image")
        return pic
