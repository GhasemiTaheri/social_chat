from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Count, Q, Subquery, OuterRef, Case, When, Value
from django.db.models.functions import Coalesce, Greatest, JSONObject
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, CreateView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from chat.forms import ConversationCreateForm
from chat.models import Conversation, Participant, Message
from chat.serializers import ConversationListSerializer, SendMessageSerializer, ConversationInputSerializer, \
    ConversationRetrieveSerializer
from django.conf import settings
from utilities.paginator.pagination import MessagePagination
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
    search_fields = ('^title',)

    def get_serializer_class(self):
        if self.action.lower() == 'list':
            return ConversationListSerializer

        elif self.action.lower() == 'retrieve':
            return ConversationRetrieveSerializer

        elif self.action.lower() in ['create', 'update']:
            return ConversationInputSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        current_user = self.request.user

        queryset = Conversation.objects.filter(participant__user_id=current_user.id)

        if self.action in ['search', 'join']:
            return (Conversation.objects
                    .exclude(id__in=Subquery(queryset.values('id')))
                    .order_by('id'))

        if self.action.lower() == 'list':
            # Subquery to get the last message data
            last_message_subquery = (Message.objects
                                     .filter(conversation=OuterRef('pk'))
                                     .order_by('-create_at')[:1])

            other_participant = (Participant.objects
                                 .filter(Q(conversation_id=OuterRef('pk')) & ~Q(user_id=current_user.id))
                                 .annotate(participant_info=JSONObject(username='user__username',
                                                                       first_name="user__first_name",
                                                                       last_name="user__last_name",
                                                                       avatar="user__avatar")))

            return (queryset
                    .annotate(last_message_date=Greatest(last_message_subquery.values('create_at'),
                                                         Max('created_at')),
                              last_message_text=Subquery(last_message_subquery.values('text')))
                    .annotate(unread_message_count=Count('message',
                                                         Q(message__create_at__gt=Coalesce(
                                                             'participant__last_read',
                                                             'participant__created_at'))
                                                         ))
                    .annotate(conversation_name=Case(When(conversation_type=Conversation.SINGLE,
                                                          then=Subquery(
                                                              other_participant.values('participant_info')))
                                                     ))
                    .order_by('last_message_date'))

        if self.action.lower() == 'retrieve':
            return queryset.annotate(participant_count=Case(
                When(conversation_type=Conversation.GROUP, then=Count('participant')),
                default=Value(2)
            ))

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj: Conversation = self.perform_create(serializer)

        channel_layer = get_channel_layer()
        for i in obj.participant_set.all():
            participant_channel_name = settings.REDIS_SERVER.get(f'channel_user_{i.user_id}')
            if participant_channel_name:
                async_to_sync(channel_layer.group_add)(str(obj.id), participant_channel_name)

        async_to_sync(channel_layer.group_send)(str(obj.id), {
            'type': 'new.message',
            'message': {
                'event_type': 'conversation_add',
                'data': serializer.data
            }
        })

        return Response(status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        return serializer.save()


@action(methods=['get'], detail=True, serializer_class=SendMessageSerializer,
        pagination_class=MessagePagination)
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
    current_user = request.user
    obj: Conversation = self.get_object()
    Participant.objects.create(user=current_user, conversation=obj)

    try:
        channel_layer = get_channel_layer()
        participant_channel_name = settings.REDIS_SERVER.get(f'channel_user_{current_user.id}')
        if participant_channel_name:
            async_to_sync(channel_layer.group_add)(str(obj.id), participant_channel_name)

            async_to_sync(channel_layer.send)(participant_channel_name, {
                'type': 'new.message',
                'message': {
                    'event_type': 'conversation_add',
                    'data': self.get_serializer(instance=obj).data
                }
            })
    except:
        pass

    return Response(status=status.HTTP_200_OK)


@action(methods=['post'], detail=True)
def read_message(self, request, pk, *args, **kwargs):
    Participant.objects.filter(conversation_id=pk, user=request.user).update(last_read=timezone.now())
    return Response(status=status.HTTP_200_OK)


@action(methods=['delete'], detail=True)
def leave_conversation(self, request, pk, *args, **kwargs):
    current_user = request.user
    obj = self.get_object()

    try:
        channel_layer = get_channel_layer()
        message_payload = {
            'type': 'new.message',
            'message': {
                'event_type': 'conversation_remove',
                'data': self.get_serializer(instance=obj).data
            }
        }

        if (obj.conversation_type == Conversation.SINGLE
                or (obj.conversation_type == Conversation.GROUP and obj.creator == current_user)):

            async_to_sync(channel_layer.group_send)(str(obj.id), message_payload)

            for participant in obj.participant_set.all():
                async_to_sync(channel_layer.group_discard)(str(obj.id), f"channel_user_{participant.user_id}")

            obj.delete()
        else:
            participant_channel_name = settings.REDIS_SERVER.get(f'channel_user_{current_user.id}')
            if participant_channel_name:
                async_to_sync(channel_layer.send)(participant_channel_name, message_payload)
                async_to_sync(channel_layer.group_discard)(str(obj.id), participant_channel_name)

            obj.participant_set.remove(current_user)

    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_204_NO_CONTENT)
