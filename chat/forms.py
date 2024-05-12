from django.forms import ModelForm

from chat.models import Conversation, Participant


class ConversationCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ConversationCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Conversation
        fields = ('title',)

    def save(self, commit=True):
        instance: Conversation = super().save(commit=False)

        current_user = self.request.user
        instance.creator = current_user
        instance.conversation_type = Conversation.GROUP
        instance.save()

        # add group creator to his/her new group
        Participant.objects.create(user=current_user, conversation=instance)

        return instance
