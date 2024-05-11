from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf.urls.static import static
from django.views.generic import TemplateView

from socialmedia import settings

from user.views import register, CustomPasswordChangeView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 3rd urls
    path('', include('django.contrib.auth.urls')),
    path('sing-up/', register, name="register"),
    path('password/',
         CustomPasswordChangeView.as_view(success_url=reverse_lazy('user:user_update'),
                                          template_name='registration/password-change.html'),
         name='password_change'),

    # local urls
    path('', TemplateView.as_view(template_name='user/landing.html'), name="index"),
    path('chat/', include('chat.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
