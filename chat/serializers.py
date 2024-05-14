from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from chat.models import Participant, Message


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
