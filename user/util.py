from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def reset_pass_email(user):
    subject = "Password Reset Requested"
    email_template_name = "registration/password_reset_email.txt"
    c = {
        "email": user.email,
        'domain': '127.0.0.1:8000',
        'site_name': 'socialchat',
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        'token': default_token_generator.make_token(user),
        'protocol': 'http',
    }
    email = render_to_string(email_template_name, c)
    try:
        send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
        return True
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
