from django.contrib import admin

from chat.models import Message, GroupConversation, PrivateConversation, Participant

admin.site.register(Participant)
admin.site.register(Message)


@admin.register(GroupConversation)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('title', 'member_count')
    search_fields = ('title',)
    # todo: change form field and set default for conversation_type and add inline 10 last message


@admin.register(PrivateConversation)
class PrivateChatAdmin(admin.ModelAdmin):
    list_display = ('title', 'participants')
    # todo: change form field and set default for conversation_type and add inline 10 last message
