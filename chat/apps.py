from django.apps import AppConfig


class ChatConfig(AppConfig):
    name = 'chat'
    verbose_name = '聊天房间'
    app_icon = 'fa fa-line-chart'

    def ready(self):
        import chat.receivers
