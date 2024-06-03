from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin

from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import ReadOnlyModelViewSet

from user.forms import UserRegisterForm
from user.models import User
from user.serializers import UserUpdateSerializer, PublicUserSerializer
from utilities.view.ViewMixin import SearchMixin


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


class UserReadViewSet(SearchMixin, ReadOnlyModelViewSet):
    serializer_class = PublicUserSerializer
    queryset = User.objects.all()
    search_fields = ('^username',)
