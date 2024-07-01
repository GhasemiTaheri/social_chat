import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker()


@pytest.mark.django_db
def test_signup_view(client):
    url = reverse('user:register')
    data = {
        'username': fake.user_name(),
        'password1': 'testpassword123',
        'password2': 'testpassword123',
        'email': fake.email()
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirects after successful signup
    assert User.objects.filter(username=data['username']).exists()


@pytest.mark.django_db
def test_password_reset_view(client, django_user_model):
    user = django_user_model.objects.create_user(username='testuser',
                                                 email='testuser@example.com',
                                                 password='testpassword123')
    client.login(username='testuser', password='testpassword123')

    url = reverse('password_reset')
    data = {'email': user.email}
    response = client.post(url, data)
    assert response.status_code == 302  # Redirects after successful password reset request


@pytest.mark.django_db
def test_user_update_destroy_api_view(client, django_user_model):
    user = django_user_model.objects.create_user(username='testuser',
                                                 email='testuser@example.com',
                                                 password='testpassword123')
    client.login(username='testuser', password='testpassword123')

    url = reverse('user:user_update')
    data = {'first_name': 'new name'}
    response = client.patch(url, data, content_type='application/json;charset=UTF-8')
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == 'new name'

    response = client.delete(url)
    assert response.status_code == 204
    assert not User.objects.filter(username='newusername').exists()


@pytest.mark.django_db
def test_user_read_view_set(client, django_user_model):
    django_user_model.objects.create_user(username='testuser',
                                          email='testuser@example.com',
                                          password='testpassword123')
    client.login(username='testuser', password='testpassword123')

    user1 = django_user_model.objects.create_user(username='user1', email='user1@example.com', password='password')
    django_user_model.objects.create_user(username='user2', email='user2@example.com', password='password')

    url = reverse('user:user-list')
    response = client.get(url, {'search': 'user1'})
    assert response.status_code == 200
    data = response.json()
    assert data['results'][0]['display_name'] == user1.display_name
