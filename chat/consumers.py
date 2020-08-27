import json
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User, AnonymousUser
from django.db.models import Q

from chat.chat_msg import ChaosBody
from chat.models import ChatLog, ChatRoom
from chat.serializers import ListChatRoomSerializers, FriendsSerializers2
from chatRobot.music_robot import MusicRobot
from dj_chat.util import ChatCache
from utils.chatrobot import talk_with_me


class ChatConsumer(AsyncWebsocketConsumer):
    """聊天Websocket"""

    def __init__(self, *args, **kwargs):
        super(ChatConsumer, self).__init__(*args, **kwargs)
        self.request_user = self.scope.get("user") or AnonymousUser()
        self.room_group_name = 'pubilc_chat'
        self.fun_prefix = 'action_'
        self.chaos = None
        self.user_uid = self.request_user.profile.unicode_id

    async def connect(self):
        # 游客拒绝
        if self.request_user.is_anonymous:
            await self.close()
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 群组聊天
    async def action_chat_message(self):
        now = datetime.now()
        room_orm = ChatRoom.objects.filter(channel_no=self.chaos.channel_no).first()
        print(self.chaos.channel_no)
        room_type = room_orm.chat_type if room_orm else 'ERROR'
        if room_type == 'ROBOT':
            # 与机器人聊天记录
            ChatLog.objects.create(chat_datetime=now,
                                   content=self.chaos.message,
                                   msg_type='chat_message',
                                   who_said=self.request_user,
                                   said_to_id=self.request_user.id,
                                   said_to_room=room_orm)
            robot_msg, msg_type = talk_with_me(self.chaos.message)
            robot_user, _ = User.objects.get_or_create(username='robot')

            ChatLog.objects.create(chat_datetime=now,
                                   content=robot_msg,
                                   msg_type=msg_type,
                                   who_said=robot_user,
                                   said_to_id=self.request_user.id,
                                   said_to_room=room_orm)
            self.chaos.data.update(
                {
                    'type': 'chat_message',
                    'message': robot_msg,
                    'send_time': now.strftime('%p %H:%M'),
                    'user_uid': 'robot',
                    'img_path': 'http://cdn.xuebai.wang/robot.png'
                }
            )
            await self.channel_layer.group_send(self.room_group_name, self.chaos.data)
        elif room_type == 'COMMON':
            self.chaos.data.update(
                {
                    'type': 'chat_message',
                    'send_time': now.strftime('%p %H:%M'),
                    'user_uid': self.user_uid,
                }
            )
            if self.chaos.message:
                ChatLog.objects.create(chat_datetime=now,
                                       content=self.chaos.message,
                                       msg_type='chat_message',
                                       who_said=self.request_user,
                                       said_to_id=self.request_user.id,
                                       said_to_room=room_orm)
            await self.channel_layer.group_send(self.room_group_name, self.chaos.data)
        elif room_type == 'MUSIC':
            await self.action_chat_music()
            if self.chaos.message:
                ChatLog.objects.create(chat_datetime=now,
                                       content=self.chaos.message,
                                       msg_type='chat_message',
                                       who_said=self.request_user,
                                       said_to_id=self.request_user.id,
                                       said_to_room=room_orm)

    async def action_chat_music(self):
        now = datetime.now()
        now_song_id = self.chaos.now_song_id
        action = self.chaos.action
        message = self.chaos.message
        command = self.chaos.command
        msg_type = 'chat_music'
        aplayer_data = []
        if command == 'init_data':
            aplayer_data = MusicRobot().get_now_song_data_list()
            command = 'init_data'
            # 询问其他人进度
        elif '点歌' in message:
            message = message.replace('点歌', '', 1).strip()
            select_music_source = self.chaos.select_music_source
            if select_music_source == '网易云音乐':
                song_info = MusicRobot().pick_a_song(message)
            elif select_music_source == 'QQ音乐':
                song_info = MusicRobot().pick_a_song_qq_music(message)
            else:
                raise Exception('不支持的音乐源')
            # 找不到歌曲，或歌曲已存在
            if not song_info:
                command = 'tips'
                aplayer_data = '找不到歌曲，或歌曲已存在'
            else:
                aplayer_data = [song_info]
                command = 'add_song'
        elif "切歌" in message:
            MusicRobot().switch_next_song(now_song_id)
            command = 'switch_next_song'
        elif command == 'reload_song_url':
            music_robot = MusicRobot()
            new_song_url = music_robot.get_song_url(now_song_id)
            if not new_song_url:
                music_robot.del_song_data(now_song_id)
                command = 'tips'
                aplayer_data = "没版权歌曲，请切换音乐源"
            else:
                now_data = music_robot.get_song_data_index(now_song_id)
                now_data['url'] = new_song_url
                music_robot.upload_song_data(now_song_id, now_data)
                aplayer_data = new_song_url
        elif command == 'remove_song':
            MusicRobot().del_song_data(self.chaos.last_song_id)
            return
        elif command == 'ack_song_process':
            print('询问其他人播放进度')
        elif command == 'syn_song_process':
            print('回答自己歌曲播放进度', self.request_user.profile.nick_name, message)
            # todo 改为自己的 return
            try:
                if float(self.chaos.current_time) < 1:
                    return
                aplayer_data = self.chaos.current_time
            except:
                import traceback
                traceback.print_exc()
        elif command == 'update_song_time':
            MusicRobot().update_song_data_song_process(now_song_id, 'song_process', self.chaos.current_time)
            return
        else:
            msg_type = 'chat_message'
            aplayer_data = message
        # print('>>>当前歌单\n', aplayer_data)
        self.chaos.data.update(
            {
                'type': 'chat_message',
                'send_time': now.strftime('%p %H:%M'),
                'user_uid': self.user_uid,
                'action': msg_type,
                'command': command,
                'aplayer_data': aplayer_data
            }
        )
        print(self.chaos.data)
        await self.channel_layer.group_send(self.room_group_name, self.chaos.data)

    def no_such_action(self):
        raise Exception('no such action')

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        # 接收参数
        text_data_dict = json.loads(text_data) or {}
        try:
            self.chaos = ChaosBody(data=text_data_dict)
        except AssertionError as e:
            print(str(e))
            import traceback
            traceback.print_exc()
            return
        action = self.chaos.action

        now = datetime.now()
        # 初始化返回
        action_func = getattr(self, self.fun_prefix + action, self.no_such_action)
        await action_func()

        # elif chaos.msg_type == 'chat_info':
        #     await self.channel_layer.group_send(
        #         self.room_group_name,
        #         {
        #             'type': 'chat_message',
        #             'message': message,
        #             'user_id': str(self.request_user.id),
        #             'send_time': now.strftime('%p %H:%M'),
        #             'msg_type': msg_type,
        #         }
        #     )

        # Receive message from room group

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))


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
