from django.forms import ModelForm, ValidationError

from chat.models import Conversation, Participant


class ConversationCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ConversationCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Conversation
        fields = ('title', 'avatar')

    def clean_avatar(self):
        pic = self.cleaned_data.get("avatar")
        if pic:
            if pic.size > 1000000:
                raise ValidationError("Image size is too large, please select another image")
        return pic

    def save(self, commit=True):
        instance: Conversation = super().save(commit=False)

        current_user = self.request.user
        instance.creator = current_user
        instance.conversation_type = Conversation.GROUP
        instance.save()

        # add group creator to his/her new group as participant.
        Participant.objects.create(user=current_user, conversation=instance)

        return instance
