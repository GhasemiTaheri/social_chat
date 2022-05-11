from django.forms import ModelForm, forms

from chat.models import Group


class GroupCreate(ModelForm):
    class Meta:
        model = Group
        fields = ("name", "avatar")

    def clean_avatar(self):
        pic = self.cleaned_data.get("avatar")
        if pic:
            if pic.size > 1000000:
                raise forms.ValidationError("Image size is too large, please select another image")
        return pic
