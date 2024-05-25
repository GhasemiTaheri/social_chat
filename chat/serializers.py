from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty

from chat.models import Participant, Message, Conversation
from user.serializers import MessageSenderSerializer


class ConversationSerializer(serializers.ModelSerializer):
    unread_messages = serializers.SerializerMethodField(method_name="get_unread_messages")
    last_message = serializers.SerializerMethodField(method_name="get_last_message")

    class Meta:
        model = Conversation
        fields = ('id', 'title', 'creator', 'avatar', 'conversation_type', 'unread_messages', 'last_message')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)

        try:
            self.request = self.context.get('request')
        except:
            pass

    def get_unread_messages(self, obj: Conversation):
        """
        Because each user has different unread messages than the other,
        we need to get the current user and then call the corresponding functions.
        """
        assert self.request is not None, "Request is required"

        return obj.unread_message_count(self.request.user)

    def get_last_message(self, obj: Conversation):
        message = obj.last_message
        if message:
            return message.text
        else:
            return ''

    def to_representation(self, instance: Conversation):
        assert self.request is not None, "Request is required"

        representation = super().to_representation(instance)

        if instance.conversation_type == instance.SINGLE:
            """
            If there is a private conversation.
            We need to display the profile picture and name of the user chatting with the current user.
            """
            other_participant = instance.participant_set.exclude(user=self.request.user).first().user
            representation['title'] = other_participant.get_full_name() or other_participant.username
            try:
                representation['avatar'] = instance.get_avatar(other_participant)
            except Exception as e:
                representation['avatar'] = None
        else:
            representation['avatar'] = instance.get_avatar()

        return representation


class ReceiveMessageSerializer(serializers.Serializer):
    conversation = serializers.UUIDField(required=True)
    message = serializers.CharField(required=True)

    def validate(self, attrs):
        user = self.context['request'].get('user')
        if not Participant.objects.filter(conversation_id=attrs.get('conversation'), user=user).aexists():
            raise ValidationError('You do not have permission to perform this action.')

        return attrs


class SendMessageSerializer(serializers.ModelSerializer):
    sender = MessageSenderSerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
