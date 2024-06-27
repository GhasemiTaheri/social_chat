from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField

from chat.models import Participant, Message, Conversation, PrivateConversation
from user.serializers import MessageSenderSerializer


class ConversationBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('id', 'title', 'avatar', 'conversation_type')

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)

        try:
            self.request = self.context.get('request')
            self.current_user = self.request.user
        except:
            pass


class ConversationListSerializer(ConversationBaseSerializer):
    title = serializers.SerializerMethodField(method_name='get_title')
    avatar = serializers.SerializerMethodField(method_name='get_avatar')
    unread_messages = SerializerMethodField(method_name="get_unread_messages")
    last_message = SerializerMethodField(method_name="get_last_message")

    class Meta(ConversationBaseSerializer.Meta):
        model = Conversation
        fields = ConversationBaseSerializer.Meta.fields + ('unread_messages', 'last_message')

    def get_title(self, obj: Conversation):
        if obj.conversation_type == Conversation.GROUP:
            return obj.title

        if hasattr(obj, 'conversation_name'):
            if obj.conversation_name.get('first_name') and obj.conversation_name.get('last_name'):
                return f"{obj.conversation_name.get('first_name')} {obj.conversation_name.get('last_name')}"

            return obj.conversation_name.get('username')
        else:
            return obj.participant_set.exclude(user=self.request.user).first().user.display_name

    def get_avatar(self, obj: Conversation):
        if obj.conversation_type == Conversation.GROUP:
            return obj.avatar.url if obj.avatar else None

        if hasattr(obj, 'conversation_name'):
            return obj.conversation_name.get('avatar') or None
        else:
            other_participants = (obj.participant_set
                                  .exclude(user=self.request.user)
                                  .values('user__avatar')[:1])[0]

            return other_participants.get('user__avatar') or None

    def get_unread_messages(self, obj: Conversation):
        """
        Because each user has different unread messages than the other,
        we need to get the current user and then call the corresponding functions.
        """
        if hasattr(obj, 'unread_message_count'):
            return obj.unread_message_count

        return obj.unread_message_count(self.request.user)

    def get_last_message(self, obj: Conversation):
        if hasattr(obj, 'last_message_text'):
            last_message = str(obj.last_message_text) if obj.last_message_text else ''
        else:
            last_message = str(obj.last_message.text) if obj.last_message else ''

        return last_message


class ConversationRetrieveSerializer(ConversationBaseSerializer):
    member_count = serializers.SerializerMethodField(method_name='get_member_count')

    class Meta(ConversationBaseSerializer.Meta):
        model = Conversation
        fields = ConversationBaseSerializer.Meta.fields + ('member_count',)

    def get_member_count(self, obj: Conversation):
        if hasattr(obj, 'participant_count'):
            return obj.participant_count

        return obj.member_count


class ConversationInputSerializer(ConversationBaseSerializer):
    members = PrimaryKeyRelatedField(required=False, many=True, queryset=get_user_model().objects.all())

    class Meta(ConversationBaseSerializer.Meta):
        model = Conversation
        fields = ConversationBaseSerializer.Meta.fields + ('members',)
        extra_kwargs = {
            'title': {'required': False},
            'conversation_type': {'required': True},
        }

    def validate(self, attrs):
        if attrs.get('conversation_type') == Conversation.SINGLE:

            if len(attrs.get('members')) > 1:
                raise ValidationError("You can't send messages to multiple people in private mode!")
            elif len(attrs.get('members')) < 1:
                raise ValidationError("You have to pick at least one!")

            if attrs.get('members')[0] == self.current_user:
                raise ValidationError("You can't start a conversation with yourself!")

            queryset = PrivateConversation.objects.private_conversation_exists(self.current_user,
                                                                               attrs.get('members')[0])
            if queryset:
                raise ValidationError('This conversation has already been created!')

        return attrs

    def create(self, validated_data):
        members = validated_data.pop('members')

        if validated_data['conversation_type'] == 'si':
            validated_data['title'] = "single conversation"

        validated_data['creator'] = self.current_user
        conversation = super().create(validated_data)

        # add conversation starter as participant
        Participant.objects.create(user=self.current_user, conversation=conversation)
        for i in members:
            Participant.objects.create(user=i, conversation=conversation)

        return conversation


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
