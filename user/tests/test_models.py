import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from chat.models import Participant, Message, Conversation

User = get_user_model()


@pytest.mark.django_db
def test_user_display_name():
    user = User.objects.create_user(username='testuser', first_name='Test', last_name='User')
    assert user.display_name == 'Test User'

    user.first_name = ''
    user.last_name = ''
    user.save()
    assert user.display_name == 'testuser'


@pytest.mark.django_db
def test_user_get_statics():
    user = User.objects.create_user(username='testuser')
    conversation = Conversation.objects.create()
    participant = Participant.objects.create(user=user, conversation=conversation)
    Message.objects.create(sender=user, conversation=conversation, text='Test message')

    stats = user.get_statics

    assert stats['message_count'] == 1
    assert stats['conversation_count'] == 1
    assert stats['friends_count'] == 0  # Assuming no friends in the conversation


@pytest.mark.django_db
def test_user_last_online():
    user = User.objects.create_user(username='testuser')
    now = timezone.now()
    user.last_online = now
    user.save()
    assert user.last_online == now
