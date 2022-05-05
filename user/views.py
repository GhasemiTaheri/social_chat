from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse

from user.forms import UserRegisterForm


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
