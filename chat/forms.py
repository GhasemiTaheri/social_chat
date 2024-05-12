from django.forms import ModelForm

from chat.models import Conversation


class ConversationCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ConversationCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Conversation
        fields = ('title',)

    def save(self, commit=True):
        instance: Conversation = super().save(commit=False)
        instance.creator = self.request.user
        instance.conversation_type = Conversation.GROUP
        return instance
