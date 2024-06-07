from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from chat.forms import ConversationCreateForm
from chat.models import Conversation, Participant, PrivateConversation
from chat.serializers import ConversationSerializer, SendMessageSerializer, ConversationCreateSerializer
from socialmedia.settings import REDIS_SERVER as redis_db
from utilities.view.ViewMixin import SearchMixin


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


class ConversationViewSet(SearchMixin, viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    search_fields = ('^title',)

    def get_queryset(self):
        current_user = self.request.user

        if self.action in ['search', 'join']:
            return Conversation.objects.exclude(participant__user_id__in=[self.request.user.id]).order_by('id')

        return (Conversation.objects.filter(participant__user_id=current_user.id)
                .annotate(last_message_date=Max('message__create_at'))
                .distinct()
                .order_by('-last_message_date'))

    def get_serializer_class(self):

        if self.action.lower() in ['create']:
            return ConversationCreateSerializer

        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get('conversation_type') == Conversation.SINGLE:
            current_user = request.user
            other_participant = serializer.validated_data.get('members')[0]
            queryset = PrivateConversation.objects.private_conversation_exists(current_user, other_participant)
            if queryset:
                return Response()

        obj: Conversation = self.perform_create(serializer)

        channel_layer = get_channel_layer()
        for i in obj.participant_set.all():
            participant_channel_name = redis_db.get(f'channel_user_{i.user_id}')

            if participant_channel_name:
                async_to_sync(channel_layer.group_add)(str(obj.id), participant_channel_name)

        async_to_sync(channel_layer.group_send)(str(obj.id), {
            'type': 'new.message',
            'message': {
                'event_type': 'conversation_add',
                'data': serializer.data
            }
        })

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        return serializer.save()

    @action(methods=['get'], detail=True, serializer_class=SendMessageSerializer)
    def get_messages(self, request, *args, **kwargs):
        queryset = self.get_object().message_set.all().order_by('-create_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=True)
    def join(self, request, *args, **kwargs):
        obj = self.get_object()
        Participant.objects.create(user=request.user, conversation=obj)

        return Response(status=status.HTTP_200_OK)
