from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

from django.urls import reverse_lazy
from django.views.generic import UpdateView, FormView, CreateView

from user.forms import UserRegisterForm, UpdateUserProfile


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


class UserUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UpdateUserProfile
    template_name = 'user/profile-update.html'
    success_url = reverse_lazy('chat:dashboard')

    def get_object(self, queryset=None):
        return self.request.user
