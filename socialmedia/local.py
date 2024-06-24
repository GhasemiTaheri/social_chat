from socialmedia.base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    *INSTALLED_APPS,
    "silk",
]
MIDDLEWARE = [
    'silk.middleware.SilkyMiddleware',
    *MIDDLEWARE,
]
SILKY_PYTHON_PROFILER = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
