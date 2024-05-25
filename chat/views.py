from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from chat.forms import ConversationCreateForm
from chat.models import Conversation
from chat.serializers import ConversationSerializer, SendMessageSerializer


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

    @action(methods=['get'], detail=True, serializer_class=SendMessageSerializer)
    def get_messages(self, request, *args, **kwargs):
        queryset = self.get_object().message_set.all().order_by('-create_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
