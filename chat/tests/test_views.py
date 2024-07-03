import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from chat.models import Conversation, Participant, Message

User = get_user_model()


@pytest.mark.django_db
def test_dashboard_view(client):
    user = User.objects.create_user(username='testuser', password='password')
    client.login(username='testuser', password='password')

    url = reverse('chat:dashboard')
    response = client.get(url)
    assert response.status_code == 200
    assert 'chat/dashboard.html' in [t.name for t in response.templates]


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='password')


@pytest.fixture
def user2():
    return User.objects.create_user(username='user2', password='password')


@pytest.fixture
def conversation(user, user2):
    conversation = Conversation.objects.create(title='Test Conversation', creator=user,
                                               conversation_type=Conversation.SINGLE)
    Participant.objects.create(user=user, conversation=conversation)
    Participant.objects.create(user=user2, conversation=conversation)
    return conversation


@pytest.fixture
def group_conversation(user, user2):
    conversation = Conversation.objects.create(title='Test Group',
                                               creator=user,
                                               conversation_type=Conversation.GROUP)
    Participant.objects.create(user=user, conversation=conversation)
    return conversation


@pytest.mark.django_db
def test_list_conversations(api_client, user, conversation):
    api_client.login(username='testuser', password='password')
    url = reverse('chat:conversation-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data is not None


@pytest.mark.django_db
def test_retrieve_conversation(api_client, user, conversation):
    api_client.login(username='testuser', password='password')
    url = reverse('chat:conversation-detail', args=[conversation.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['title'] == conversation.get_single_conversation_title(user)


@pytest.mark.django_db
def test_create_group_conversation(api_client, user):
    api_client.login(username='testuser', password='password')
    url = reverse('chat:conversation-list')
    data = {
        'title': 'New Conversation',
        'conversation_type': Conversation.GROUP,
    }
    response = api_client.post(url, data)
    assert response.status_code == 201
    assert Conversation.objects.filter(title='New Conversation').exists()


@pytest.mark.django_db
def test_create_single_conversation(api_client, user, user2):
    api_client.login(username='testuser', password='password')
    url = reverse('chat:conversation-list')
    data = {
        'conversation_type': Conversation.SINGLE,
        'members': [user2.id]
    }
    response = api_client.post(url, data)
    assert response.status_code == 201
    assert Conversation.objects.filter(conversation_type=Conversation.SINGLE).exists()


@pytest.mark.django_db
def test_join_group_conversation(api_client, user2, group_conversation):
    api_client.login(username='user2', password='password')
    url = reverse('chat:conversation-join', args=[group_conversation.id])
    response = api_client.post(url)
    assert response.status_code == 200
    assert Participant.objects.filter(user=user2, conversation=group_conversation).exists()


@pytest.mark.django_db
def test_join_single_conversation(api_client, user, conversation):
    new_single_con = Conversation.objects.create(title='test single',
                                                 creator=user,
                                                 conversation_type=Conversation.SINGLE)
    api_client.login(username='user2', password='password')
    url = reverse('chat:conversation-join', args=[new_single_con.id])
    response = api_client.post(url)
    assert response.status_code == 400


@pytest.mark.django_db
def test_leave_conversation(api_client, user, conversation):
    api_client.login(username='testuser', password='password')
    url = reverse('chat:conversation-leave-conversation', args=[conversation.id])
    response = api_client.delete(url)
    assert response.status_code == 204
    assert not Participant.objects.filter(user=user, conversation=conversation).exists()


@pytest.mark.django_db
def test_read_message(api_client, user, conversation):
    message = Message.objects.create(conversation=conversation, sender=user, text='Test message')
    api_client.login(username='testuser', password='password')
    url = reverse('chat:conversation-read-message', args=[conversation.id])
    response = api_client.post(url)
    assert response.status_code == 200
    participant = Participant.objects.get(user=user, conversation=conversation)
    assert participant.last_read is not None


@pytest.mark.django_db
def test_get_messages(api_client, user, conversation):
    message = Message.objects.create(conversation=conversation, sender=user, text='Test message')
    api_client.login(username='testuser', password='password')
    url = reverse('chat:conversation-get-messages', args=[conversation.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 1
