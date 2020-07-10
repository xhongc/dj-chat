import json
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from chat.models import ChatLog, ChatRoom
from dj_chat.util import ChatCache
from utils.chatrobot import sizhi


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(ChatConsumer, self).__init__(*args, **kwargs)
        self.room_name = 'chat'
        self.room_group_name = 'chat'
        self.chat_room_model = None

    async def connect(self):
        room_channel_no = self.scope['url_route']['kwargs']['room_name']
        request_user = self.scope["user"]
        # 游客拒绝
        if request_user.is_anonymous:
            # Reject the connection
            await self.close()
        # 必须是我加入的频道
        elif room_channel_no in request_user.profile.get_my_chat_room():
            self.room_name = room_channel_no
            self.room_group_name = 'chat_%s' % self.room_name
            # 加入成员保存字典 redis缓存中
            ChatCache().append(self.room_group_name, request_user.profile.unicode_id)
            print('UID:%s加入房间(%s),剩余:%s' % (
                self.scope["user"].profile.unicode_id, self.room_group_name,
                ChatCache().get_cache(self.room_group_name)))
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
        # 机器人回复频道
        elif room_channel_no == 'GP_robot':
            self.room_name = room_channel_no
            self.room_group_name = 'chat_%s' % self.room_name

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group 缓存中清理
        ChatCache().remove(self.room_group_name, self.scope["user"].profile.unicode_id)
        print('UID:%s离开房间(%s),剩余:%s' % (
            self.scope["user"].profile.unicode_id, self.room_group_name, ChatCache().get_cache(self.room_group_name)))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        msg_type = text_data_json['msg_type']
        send_user_nick_name = text_data_json.get('send_user_nick_name', '') or ''
        chat_user = self.scope.get('user')
        send_time = datetime.now()
        # 机器人 加思知回复
        if self.room_name == 'GP_robot' and msg_type == 'chat_message':
            self.chat_room_model = ChatRoom.objects.filter(channel_no=self.room_name).first()
            robot_msg = sizhi(message)
            robot_user, _ = User.objects.get_or_create(username='robot')
            robot_send_time = datetime.now()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': robot_msg,
                    'user_id': 'robot',
                    'send_time': robot_send_time.strftime('%p %H:%M'),
                    'msg_type': msg_type,
                    'username': self.scope.get('user').username
                }
            )
            if message:
                ChatLog.objects.create(chat_datetime=robot_send_time,
                                       content=message,
                                       msg_type=msg_type,
                                       who_said=chat_user,
                                       said_to_id=chat_user.id,
                                       said_to_room=self.chat_room_model)

                ChatLog.objects.create(chat_datetime=robot_send_time,
                                       content=robot_msg,
                                       msg_type=msg_type,
                                       who_said=robot_user,
                                       said_to_id=chat_user.id,
                                       said_to_room=self.chat_room_model)
        elif msg_type == 'chat_message':
            self.chat_room_model = ChatRoom.objects.filter(channel_no=self.room_name).first()
            # Send message to room group 如果他人不在房间就单对单发通知
            if self.chat_room_model:
                menbers_list = self.chat_room_model.get_members_unicode_id()
                online_list = ChatCache().get_cache(self.room_group_name)
                outline_list = set(menbers_list) - online_list
                print('成员人数：%s\n在线人数：%s\n离线人数：%s' % (menbers_list, online_list, outline_list))
                for ntf in outline_list:
                    await self.channel_layer.group_send(
                        'notification_%s' % (ntf),
                        {
                            'type': 'push_message',
                            'message': message,
                            'user_id': str(chat_user.id),
                            'send_time': send_time.strftime('%p %H:%M'),
                            'msg_type': msg_type,
                            'channel_no': self.room_name,
                            'send_user_nick_name': send_user_nick_name,
                        }
                    )
                if message:
                    queryset = []
                    for on in online_list:
                        queryset.append(ChatLog(chat_datetime=send_time,
                                                content=message,
                                                msg_type=msg_type,
                                                who_said=chat_user,
                                                said_to=User.objects.filter(profile__unicode_id=on).first(),
                                                said_to_room=self.chat_room_model,
                                                status='read'))
                    for out in outline_list:
                        queryset.append(ChatLog(chat_datetime=send_time,
                                                content=message,
                                                msg_type=msg_type,
                                                who_said=chat_user,
                                                said_to=User.objects.filter(profile__unicode_id=out).first(),
                                                said_to_room=self.chat_room_model,
                                                status='unread'))
                    ChatLog.objects.bulk_create(queryset)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'user_id': str(chat_user.id),
                        'send_time': send_time.strftime('%p %H:%M'),
                        'msg_type': msg_type,
                    }
                )
        elif msg_type == 'chat_info':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': str(chat_user.id),
                    'send_time': send_time.strftime('%p %H:%M'),
                    'msg_type': msg_type,
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']
        send_time = event['send_time']
        type = event['type']
        msg_type = event['msg_type']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
            'send_time': send_time,
            'type': type,
            'msg_type': msg_type,
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        uid = self.scope['url_route']['kwargs']['uid']
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            self.uid = uid
            self.uid_group = 'notification_%s' % self.uid

            # Join room group
            await self.channel_layer.group_add(
                self.uid_group,
                self.channel_name
            )

            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.uid_group,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        msg_type = text_data_json['msg_type']
        send_to_user_uid = text_data_json['send_to_user_uid']
        send_user_nick_name = text_data_json.get('send_user_nick_name', '') or ''
        chat_user = self.scope.get('user')
        if msg_type == 'push_message':
            await self.channel_layer.group_send(
                self.uid_group,
                {
                    'type': msg_type,
                    'message': message,
                    'user_id': '',
                    'send_time': '',
                    'msg_type': '',
                }
            )
        elif msg_type == 'chat_message':
            request_user_uid = str(chat_user.profile.unicode_id)
            ChatLog.objects.create(chat_datetime=datetime.now(),
                                   content=message,
                                   msg_type=msg_type,
                                   who_said=chat_user,
                                   said_to=User.objects.filter(profile__unicode_id=send_to_user_uid).first(),
                                   said_together='&'.join(
                                       sorted([request_user_uid, send_to_user_uid])),
                                   status='unread'
                                   )

            await self.channel_layer.group_send(
                'notification_%s' % (send_to_user_uid),
                {
                    'type': msg_type,
                    'message': message,
                    'user_id': '',
                    'send_time': '',
                    'msg_type': '',
                    'channel_no': request_user_uid,
                    'send_user_nick_name': send_user_nick_name,
                }
            )

    async def push_message(self, event):
        channel_no = event['channel_no']
        message = event['message']
        send_user_nick_name = event['send_user_nick_name']
        chat_room = ChatRoom.objects.filter(channel_no=channel_no).first()
        await self.send(text_data=json.dumps({
            "channel_no": channel_no,
            'message': message,
            'img': chat_room.img_path,
            'send_user_nick_name': send_user_nick_name
        }))

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']
        send_time = event['send_time']
        type = event['type']
        msg_type = event['msg_type']
        channel_no = event['channel_no']
        send_user_nick_name = event['send_user_nick_name']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
            'send_time': send_time,
            'type': type,
            'msg_type': msg_type,
            'channel_no': channel_no,
            'send_user_nick_name': send_user_nick_name,
        }))
