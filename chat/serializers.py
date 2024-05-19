from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty

from chat.models import Participant, Message, Conversation


class ConversationSerializer(serializers.ModelSerializer):
    unread_messages = serializers.SerializerMethodField(method_name="get_unread_messages")

    class Meta:
        model = Conversation
        fields = ('id', 'title', 'creator', 'avatar', 'conversation_type', 'unread_messages')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)

        try:
            self.request = self.context.get('request')
        except:
            pass

    def get_unread_messages(self, obj: Conversation):
        assert self.request is not None, "Request is required"

        return obj.unread_message_count(self.request.user)

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

            if other_participant.avatar:
                representation['avatar'] = self.request.build_absolute_uri(other_participant.avatar.url)
            else:
                representation['avatar'] = None

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
    class Meta:
        model = Message
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['conversation'] = str(instance.conversation_id)
        return representation
