from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from rest_framework import viewsets

from chat.forms import ConversationCreateForm
from chat.models import Conversation
from chat.serializers import ConversationSerializer


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/dashboard.html'


class GroupCreateView(LoginRequiredMixin, CreateView):
    form_class = ConversationCreateForm
    template_name = 'chat/create_group.html'
    success_url = reverse_lazy('chat:dashboard')

    def get_form_kwargs(self):
        kwargs = super(GroupCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        current_user = self.request.user
        return (Conversation.objects.filter(participant__user_id=current_user.id)
                .annotate(last_message_date=Max('message__create_at'))
                .distinct()
                .order_by('-last_message_date'))
