# social_chat
Social chat is a message app written in django and js
## Distinctiveness and Complexity
In this program, the user is able to create different groups and communicate with his/her friends in real time. Also, this program is compatible with all screens size.
## Project structure
### socialmedia module
This module includes project configs and settings.
### chat module
This module contains URLs, views, and models that we need to create groups and communicate with others.
### user module
This module is used to manage users.
## How to run
1. Create a virtual env in project folder `python -m venv venv`
2. After construction and activation venv, install requirments `pip install -r requirement.txt`
3. Create a text file named secret_key.txt next to the manage.py file. This file must contain a secret key. Like below
> 'django-insecure-tn97%=i5aa4*&6fg4eb$ysz********************'
4. Create DB: `python manage.py makemigrations` then `python manage.py migrate`
5. Create superuser user with `python manage.py createsuperuser`
6. run server `python manage.py runserver`
7. run redis on port 6379