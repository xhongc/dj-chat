import django_filters

from chat.models import ChatRoom, ChatLog


class ChatRoomFilter(django_filters.FilterSet):
    channel_no = django_filters.CharFilter()
    is_all = django_filters.CharFilter()

    class Meta:
        model = ChatRoom
        fields = ['channel_no','is_all']


class ChatLogFilter(django_filters.FilterSet):
    said_to_room__channel_no = django_filters.CharFilter()

    class Meta:
        model = ChatLog
        fields = ['said_to_room__channel_no']


class PersonalChatLogFilter(django_filters.FilterSet):
    who_said__profile__unicode_id = django_filters.CharFilter()

    class Meta:
        model = ChatLog
        fields = ['who_said__profile__unicode_id']
