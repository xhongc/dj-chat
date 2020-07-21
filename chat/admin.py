from django.contrib import admin

from chat.models import ChatRoom, ChatLog, UserProfile, History


# Register your models here.
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['room_name', 'channel_no']
    list_filter = ['room_name', 'channel_no']
    search_fields = ['room_name', 'channel_no']


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    list_display = ['chat_datetime', 'content']
    list_filter = ['who_said', 'said_to', 'said_to_room']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'nick_name', 'unicode_id']


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['ip', 'count', 'date_created']
