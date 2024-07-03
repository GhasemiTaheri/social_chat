from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max, Count, Q, Subquery, OuterRef, Case, When, Value, F
from django.db.models.functions import Coalesce, Greatest, JSONObject
from django.utils import timezone
from django.views.generic import TemplateView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from chat.models import Conversation, Participant, Message
from chat.serializers import ConversationListSerializer, SendMessageSerializer, ConversationInputSerializer, \
    ConversationRetrieveSerializer, ConversationBaseSerializer
from utilities.paginator.pagination import MessagePagination
from utilities.socket.socket_mixin import WebSocketMixin
from utilities.view.viewset_mixin import SearchMixin


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'chat/dashboard.html'


class ConversationViewSet(WebSocketMixin, SearchMixin, viewsets.ModelViewSet):
    serializer_class = ConversationBaseSerializer
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

        other_participant = (Participant.objects
                             .filter(Q(conversation_id=OuterRef('pk')) & ~Q(user_id=current_user.id))
                             .annotate(participant_info=JSONObject(username='user__username',
                                                                   first_name="user__first_name",
                                                                   last_name="user__last_name",
                                                                   avatar="user__avatar")))

        queryset = Conversation.objects.filter(participant__user_id=current_user.id)

        if self.action.lower() in ['search', 'join']:
            return (Conversation.objects
                    .exclude(id__in=Subquery(queryset.values('id')))
                    .order_by('id'))

        if self.action.lower() == 'list':
            # Subquery to get the last message data
            last_message_subquery = (Message.objects
                                     .filter(conversation=OuterRef('pk'))
                                     .order_by('-create_at')[:1])

            return (queryset
                    .defer('creator', 'created_at', 'updated_at')
                    .annotate(last_message_date=Greatest(last_message_subquery.values('create_at'),
                                                         Max('created_at')),
                              last_message_text=Subquery(last_message_subquery.values('text')))
                    .annotate(unread_message_count=Count('message',
                                                         Q(message__create_at__gt=Coalesce(
                                                             'participant__last_read',
                                                             'participant__created_at'))
                                                         ))
                    .annotate(conversation_name=Case(When(conversation_type=Conversation.SINGLE,
                                                          then=Subquery(other_participant.values('participant_info')))
                                                     ))
                    .order_by('last_message_date'))

        if self.action.lower() == 'retrieve':
            return (queryset
                    .defer('created_at', 'updated_at')
                    .annotate(participant_count=Case(When(conversation_type=Conversation.GROUP,
                                                          then=Count('participant')),
                                                     default=Value(2)))
                    .annotate(conversation_name=Case(When(conversation_type=Conversation.SINGLE,
                                                          then=Subquery(
                                                              other_participant.values('participant_info')))
                                                     ))
                    )
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj: Conversation = serializer.save()

        user_ids = list(obj.participant_set.all().values_list('id', flat=True))
        self.add_users_to_group(str(obj.id), user_ids, payload={
            'type': 'new.message',
            'message': {
                'event_type': 'conversation_add',
                'data': serializer.data
            }
        })

        return Response(status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=True, serializer_class=SendMessageSerializer,
            pagination_class=MessagePagination)
    def get_messages(self, request, *args, **kwargs):
        queryset = (self.get_object()
                    .message_set.all()
                    .select_related('sender')
                    .order_by('-create_at'))

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

        if obj.conversation_type == Conversation.SINGLE:
            raise ValidationError("You cannot join this conversation")

        Participant.objects.create(user=current_user, conversation=obj)
        try:
            self.add_users_to_group(str(obj.id), [current_user.id], payload={
                'type': 'new.message',
                'message': {
                    'event_type': 'conversation_add',
                    'data': self.get_serializer(instance=obj).data
                }
            })
        except Exception as e:
            print(e)
            raise

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
            payload = {
                'type': 'new.message',
                'message': {
                    'event_type': 'conversation_remove',
                    'data': self.get_serializer(instance=obj).data
                }
            }

            if (obj.conversation_type == Conversation.SINGLE
                    or obj.conversation_type == Conversation.GROUP and obj.creator == current_user):
                user_ids = list(obj.participant_set.all().values_list('id', flat=True))

                self.remove_from_group(str(obj.id), user_ids, payload=payload)
                obj.delete()
            else:
                obj.participant_set.remove(current_user)
                self.remove_from_group(str(obj.id), [current_user.id], payload=payload)
        except Exception as e:
            print(e)
            raise

        return Response(status=status.HTTP_204_NO_CONTENT)
