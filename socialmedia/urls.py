"""socialmedia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import PasswordChangeView
from django.urls import path, include, reverse_lazy
from django.conf.urls.static import static
from socialmedia import settings
from django.contrib.auth import views as auth_views

from user.views import register, CustomPasswordChangeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user.urls')),
    path('chat/', include('chat.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name='user/landing.html'), name="logout"),
    path('register/', register, name="register"),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'),
         name='password_reset_complete'),

    path('password/',
         CustomPasswordChangeView.as_view(success_url=reverse_lazy('user:user_update'),
                                          template_name='password/password-change.html'),
         name='password_change'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
