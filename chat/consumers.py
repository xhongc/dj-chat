import json
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User, AnonymousUser

from chat.models import ChatLog, ChatRoom
from chatRobot.music_robot import MusicRobot
from dj_chat.util import ChatCache
from utils.chatrobot import talk_with_me


class ChatConsumer(AsyncWebsocketConsumer):
    """聊天Websocket"""

    def __init__(self, *args, **kwargs):
        super(ChatConsumer, self).__init__(*args, **kwargs)
        self.room_channel_no = None  # 频道号
        self.room_type = None  # 类型
        self.room_group_name = None  # 类型+频道号
        self.chat_room_model = None
        self.profile_uid = None
        self.request_user = self.scope.get("user") or AnonymousUser()

    async def connect(self):

        # 游客拒绝
        if self.request_user.is_anonymous:
            await self.close()

        # 初始化信息
        self.profile_uid = self.request_user.profile.unicode_id
        # url参数上的channel_no
        self.room_channel_no = self.scope['url_route']['kwargs']['room_name']
        self.chat_room_model = ChatRoom.objects.filter(channel_no=self.room_channel_no).first()
        self.room_type = self.chat_room_model.chat_type
        # 拼接websocket组的名字
        self.room_group_name = self.room_type + '_' + self.room_channel_no
        # 初始化信息结束

        # 必须是我加入的频道
        if self.room_channel_no in self.request_user.profile.get_my_chat_room():
            # 加入成员保存字典 redis缓存中
            ChatCache(self.room_group_name).set_add(self.profile_uid)
            # 打印信息
            print('UID:%s加入房间(%s),剩余:%s' % (
                self.profile_uid, self.room_group_name,
                ChatCache(self.room_group_name).set_members()))
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        # 机器人回复频道
        elif self.room_type == 'ROBOT':
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
        ChatCache(self.room_group_name).set_remove(self.profile_uid)
        print('UID:%s离开房间(%s),剩余:%s' % (
            self.request_user.profile.unicode_id, self.room_group_name, ChatCache(self.room_group_name).set_members()))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def message_send(self, group, message):
        await self.channel_layer.group_send(group, message)

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        # 接收参数
        text_data_json = json.loads(text_data) or {}
        message = text_data_json.get('message', '')
        if message == '': return
        msg_type = text_data_json.get('msg_type')
        action = text_data_json.get('action', '')
        song_index = text_data_json.get('song_index', None)
        now_song_id = text_data_json.get('now_song_id', None)
        send_user_nick_name = text_data_json.get('send_user_nick_name', '')

        send_time = datetime.now()

        # 房间类型
        # 机器人
        if self.room_type == 'ROBOT' and msg_type == 'chat_message':
            robot_msg, msg_type = talk_with_me(message)
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
                    'username': self.request_user.username
                }
            )
            if message:
                # 与机器人聊天记录
                ChatLog.objects.create(chat_datetime=robot_send_time,
                                       content=message,
                                       msg_type=msg_type,
                                       who_said=self.request_user,
                                       said_to_id=self.request_user.id,
                                       said_to_room=self.chat_room_model)

                ChatLog.objects.create(chat_datetime=robot_send_time,
                                       content=robot_msg,
                                       msg_type=msg_type,
                                       who_said=robot_user,
                                       said_to_id=self.request_user.id,
                                       said_to_room=self.chat_room_model)
        # 普通的对话
        elif msg_type == 'chat_message':
            # Send message to room group 如果他人不在房间就单对单发通知
            if self.chat_room_model:
                # 房间成员
                menbers_list = self.chat_room_model.get_members_unicode_id()
                menbers_list = [str(i) for i in menbers_list]
                # 在线成员
                online_list = ChatCache(self.room_group_name).set_members()
                # 离线成员
                outline_list = set(menbers_list) - online_list
                print('成员人数：%s\n在线人数：%s\n离线人数：%s' % (menbers_list, online_list, outline_list))
                # 离线发通知
                for ntf in outline_list:
                    await self.channel_layer.group_send(
                        'notification_%s' % (ntf),
                        {
                            'type': 'push_message',
                            'msg_type': 'push_message',
                            'message': message,
                            'send_time': send_time.strftime('%p %H:%M'),
                            'channel_no': self.room_channel_no,
                            'user_id': str(self.request_user.id),
                            'send_user_nick_name': send_user_nick_name,
                        }
                    )
                if message:
                    queryset = []
                    for on in online_list:
                        queryset.append(ChatLog(chat_datetime=send_time,
                                                content=message,
                                                msg_type=msg_type,
                                                who_said=self.request_user,
                                                said_to=User.objects.filter(profile__unicode_id=on).first(),
                                                said_to_room=self.chat_room_model,
                                                status='read'))
                    for out in outline_list:
                        queryset.append(ChatLog(chat_datetime=send_time,
                                                content=message,
                                                msg_type=msg_type,
                                                who_said=self.request_user,
                                                said_to=User.objects.filter(profile__unicode_id=out).first(),
                                                said_to_room=self.chat_room_model,
                                                status='unread'))
                    ChatLog.objects.bulk_create(queryset)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'user_id': str(self.request_user.id),
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
                    'user_id': str(self.request_user.id),
                    'send_time': send_time.strftime('%p %H:%M'),
                    'msg_type': msg_type,
                }
            )
        elif msg_type == 'chat_music':
            aplayer_data = []
            if 'init_data' in message:
                aplayer_data = MusicRobot().get_now_song_data_list()
                action = 'init_data'
                # 询问其他人进度
            elif '点歌' in message:
                message = message.replace('点歌', '', 1).strip()
                song_info = MusicRobot().pick_a_song(message)
                # 找不到歌曲，或歌曲已存在
                if not song_info:
                    action = 'tips'
                else:
                    aplayer_data = [song_info]
                    action = 'add_song'
            elif "切歌" in message:
                MusicRobot().switch_next_song(now_song_id)
                action = 'switch_next_song'
            elif action == 'reload_song_url':
                music_robot = MusicRobot()
                music_robot.del_song_data(now_song_id)
                new_song_url = music_robot.get_song_url(now_song_id)
                if not new_song_url:
                    action = 'tips'
                else:
                    message['url'] = new_song_url
                    music_robot.upload_song_data(now_song_id, message)
                    aplayer_data = [message]
            elif action == 'remove_song':
                MusicRobot().del_song_data(now_song_id)
                return
            elif action == 'ack_song_process':
                print('询问其他人播放进度')
            elif action == 'syn_song_process':
                print('回答自己歌曲播放进度', self.request_user.profile.nick_name, message)
                # todo 改为自己的 return
                if float(message) < 1:
                    return
                aplayer_data = message
            elif action == 'quit_listen_song':
                print(message)
            elif action == 'update_song':
                MusicRobot().update_song_data_song_process(now_song_id, 'song_process', message)
                return
            else:
                msg_type = 'chat_message'
                aplayer_data = message
            print('>>>当前歌单\n', aplayer_data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': aplayer_data,
                    'msg_type': msg_type,
                    'user_id': str(self.request_user.id),
                    'send_time': '',
                    'action': action,
                    'song_index': song_index,
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        user_id = event['user_id']
        send_time = event['send_time']
        type = event['type']
        msg_type = event['msg_type']
        action = event.get('action', 'null')
        song_index = event.get('song_index', 0)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user_id': user_id,
            'send_time': send_time,
            'type': type,
            'msg_type': msg_type,
            'action': action,
            'song_index': song_index
        }))


class NotificationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super(NotificationConsumer, self).__init__(*args, **kwargs)
        self.uid = self.scope['url_route']['kwargs']['uid']

    async def connect(self):
        uid = self.scope['url_route']['kwargs']['uid']
        ChatCache('__online').set_add(uid)
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
        # ChatCache().set_remove('__online', self.uid)
        await self.channel_layer.group_discard(
            self.uid_group,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        msg_type = text_data_json['msg_type']
        send_to_user_uid = text_data_json.get('send_to_user_uid', '')
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
                    'msg_type': msg_type,
                }
            )
        elif msg_type == 'chat_message':
            request_user_uid = str(chat_user.profile.unicode_id)
            send_time = datetime.now()
            ChatLog.objects.create(chat_datetime=send_time,
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
                    'user_id': str(chat_user.id),
                    'send_time': send_time.strftime('%p %H:%M'),
                    'msg_type': msg_type,
                    'channel_no': request_user_uid,
                    'send_user_nick_name': send_user_nick_name,
                }
            )

    async def push_message(self, event):
        channel_no = event['channel_no']
        message = event['message']
        send_user_nick_name = event['send_user_nick_name']
        msg_type = event['msg_type']
        chat_room = ChatRoom.objects.filter(channel_no=channel_no).first()
        await self.send(text_data=json.dumps({
            "channel_no": channel_no,
            'message': message,
            'img': chat_room.img_path,
            'send_user_nick_name': send_user_nick_name,
            'msg_type': msg_type,
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
