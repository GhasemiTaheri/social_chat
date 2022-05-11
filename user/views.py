import os
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.shortcuts import render, redirect

from django.urls import reverse

from user.forms import UserRegisterForm, UpdateUserProfile
from user.models import User
from user.util import reset_pass_email


def index(request):
    return render(request, 'user/landing.html')


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password2')

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('chat:dashboard')

            return redirect('login')

    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {
        'register_form': form,
    })


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    if reset_pass_email(user):
                        return redirect("/password_reset/done/")
            else:
                password_reset_form.add_error('email', 'Email does not exist!')
    else:
        password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password/password_reset.html",
                  context={"password_reset_form": password_reset_form})


@login_required
def user_update(request):
    if request.method == "POST":
        user_obj = User.objects.get(id=request.user.id)
        user_form = UpdateUserProfile(request.POST, request.FILES, instance=user_obj)

        if user_form.is_valid():

            # remove user avatar from DISK
            if request.FILES:
                if request.user.avatar:
                    if not user_form.cleaned_data['avatar']:
                        os.remove(request.user.avatar.path)
                user_obj.avatar = user_form.cleaned_data['avatar']
            else:
                if request.user.avatar:
                    if not user_form.cleaned_data['avatar']:
                        os.remove(request.user.avatar.path)

            user_form.save()
            messages.success(request, "Your information updated")
            return redirect(reverse('user:user_update'))

        messages.warning(request, "please try again")
    else:
        user_form = UpdateUserProfile(instance=User.objects.get(id=request.user.id))
    return render(request, 'user/profile-update.html', {
        'profile': request.user,
        'form': user_form
    })


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    def get_context_data(self, *args, **kwargs):
        context = super(CustomPasswordChangeView, self).get_context_data(*args, **kwargs)
        context['profile'] = self.request.user
        return context
