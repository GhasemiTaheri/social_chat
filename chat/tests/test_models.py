import datetime

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from chat.models import Conversation, GroupConversation, PrivateConversation, Participant, Message

User = get_user_model()


@pytest.mark.django_db
def test_conversation_creation():
    user = User.objects.create_user(username='creator', password='password')
    conversation = Conversation.objects.create(title='Test Conversation', creator=user,
                                               conversation_type=Conversation.SINGLE)
    assert conversation.id is not None
    assert conversation.title == 'Test Conversation'
    assert conversation.creator == user
    assert conversation.conversation_type == Conversation.SINGLE


@pytest.mark.django_db
def test_member_count():
    user1 = User.objects.create_user(username='user1', password='password')
    user2 = User.objects.create_user(username='user2', password='password')
    conversation = Conversation.objects.create(title='Test Conversation', creator=user1,
                                               conversation_type=Conversation.GROUP)
    Participant.objects.create(user=user1, conversation=conversation)
    Participant.objects.create(user=user2, conversation=conversation)
    assert conversation.member_count == 2


@pytest.mark.django_db
def test_last_message():
    user = User.objects.create_user(username='user', password='password')
    conversation = Conversation.objects.create(title='Test Conversation', creator=user,
                                               conversation_type=Conversation.SINGLE)
    Message.objects.create(conversation=conversation, sender=user, text='First message')
    last_message = Message.objects.create(conversation=conversation, sender=user, text='Last message')
    assert conversation.last_message == last_message


@pytest.mark.django_db
def test_unread_message_count():
    user1 = User.objects.create_user(username='user1', password='password')
    user2 = User.objects.create_user(username='user2', password='password')

    conversation = Conversation.objects.create(title='Test Conversation', creator=user1,
                                               conversation_type=Conversation.SINGLE)
    Participant.objects.create(user=user1, conversation=conversation)
    Message.objects.create(conversation=conversation, sender=user1, text='First message')
    Message.objects.create(conversation=conversation, sender=user1, text='Second message')

    Participant.objects.create(user=user2, conversation=conversation,
                               last_read=timezone.now() - datetime.timedelta(days=1))
    assert conversation.unread_message_count(user2) == 2


@pytest.mark.django_db
def test_group_conversation():
    user = User.objects.create_user(username='user', password='password')
    group_conversation = GroupConversation.objects.create(title='Test Group', creator=user)
    assert group_conversation.id is not None
    assert group_conversation.conversation_type == Conversation.GROUP
    assert group_conversation.title == 'Test Group'


@pytest.mark.django_db
def test_private_conversation():
    user1 = User.objects.create_user(username='user1', password='password')
    user2 = User.objects.create_user(username='user2', password='password')
    private_conversation = PrivateConversation.objects.create(title='Test Private', creator=user1)
    Participant.objects.create(user=user1, conversation=private_conversation)
    Participant.objects.create(user=user2, conversation=private_conversation)
    assert private_conversation.id is not None
    assert private_conversation.conversation_type == Conversation.SINGLE
    assert private_conversation.title == 'Test Private'
    assert 'user1' in private_conversation.participants()
    assert 'user2' in private_conversation.participants()


@pytest.mark.django_db
def test_message_creation():
    user = User.objects.create_user(username='user', password='password')
    conversation = Conversation.objects.create(title='Test Conversation', creator=user,
                                               conversation_type=Conversation.SINGLE)
    message = Message.objects.create(conversation=conversation, sender=user, text='Test message')
    assert message.id is not None
    assert message.text == 'Test message'
    assert message.sender == user
    assert message.conversation == conversation


@pytest.mark.django_db
def test_participant_creation():
    user = User.objects.create_user(username='user', password='password')
    conversation = Conversation.objects.create(title='Test Conversation', creator=user,
                                               conversation_type=Conversation.SINGLE)
    participant = Participant.objects.create(user=user, conversation=conversation)
    assert participant.id is not None
    assert participant.user == user
    assert participant.conversation == conversation
