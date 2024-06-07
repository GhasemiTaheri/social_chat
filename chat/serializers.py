from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty, HiddenField, CurrentUserDefault, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField

from chat.models import Participant, Message, Conversation
from user.serializers import MessageSenderSerializer


class ConversationSerializer(serializers.ModelSerializer):
    unread_messages = SerializerMethodField(method_name="get_unread_messages")
    last_message = SerializerMethodField(method_name="get_last_message")

    class Meta:
        model = Conversation
        fields = ('id', 'title', 'creator',
                  'avatar', 'conversation_type', 'unread_messages',
                  'last_message', 'member_count')

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


class ConversationCreateSerializer(serializers.ModelSerializer):
    members = PrimaryKeyRelatedField(required=False, many=True, queryset=get_user_model().objects.all())
    creator = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'creator', 'conversation_type', 'avatar', 'members']
        extra_kwargs = {
            'title': {'required': False},
            'conversation_type': {'required': True},
        }

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)

        try:
            self.request = self.context.get('request')
        except:
            pass

    def validate(self, attrs):
        if attrs.get('conversation_type') == 'si':

            if len(attrs.get('members')) > 1:
                raise ValidationError("You can't send messages to multiple people in private mode!")
            elif len(attrs.get('members')) < 1:
                raise ValidationError("You have to pick at least one!")

            if attrs.get('creator') == attrs.get('members')[0]:
                raise ValidationError("You can't start a conversation with yourself!")

        return attrs

    def create(self, validated_data):
        current_user = self.context['request'].user

        members = validated_data.pop('members')

        if validated_data['conversation_type'] == 'si':
            validated_data['title'] = "single conversation"

        conversation = super().create(validated_data)

        # add conversation starter as participant
        Participant.objects.create(user=current_user, conversation=conversation)
        for i in members:
            Participant.objects.create(user=i, conversation=conversation)

        return conversation

    def save(self, **kwargs):
        return super().save(**kwargs)

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
    conversation = serializers.SerializerMethodField(method_name='get_conversation_uuid')

    class Meta:
        model = Message
        fields = '__all__'

    def get_conversation_uuid(self, obj: Message) -> str:
        return str(obj.conversation_id)
