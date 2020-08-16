from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer),
    re_path(r'ws/notification/(?P<uid>\w+)/$', consumers.NotificationConsumer),
]
