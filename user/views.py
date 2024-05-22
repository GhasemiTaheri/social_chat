from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from user.forms import UserRegisterForm
from user.serializers import UserUpdateSerializer


class SignUpView(CreateView):
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')
    template_name = 'user/register.html'


class PasswordResetView(LoginRequiredMixin, FormView):
    form_class = PasswordResetForm
    template_name = 'registration/password_reset.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        form.save(domain_override='socialchat.com')
        return super().form_valid(form)


class UserUpdateDestroyApiView(UpdateModelMixin, DestroyModelMixin, GenericAPIView):
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user
