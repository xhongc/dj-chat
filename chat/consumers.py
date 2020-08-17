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

    # async def connect_1(self):
    #     # 游客拒绝
    #     if self.request_user.is_anonymous:
    #         await self.close()
    #     # 初始化信息
    #     self.profile_uid = self.request_user.profile.unicode_id
    #     # url参数上的channel_no
    #     self.room_channel_no = self.scope['url_route']['kwargs']['room_name']
    #     self.chat_room_model = ChatRoom.objects.filter(channel_no=self.room_channel_no).first()
    #     self.room_type = self.chat_room_model.chat_type
    #     # 拼接websocket组的名字
    #     self.room_group_name = self.room_type + '_' + self.room_channel_no
    #     # 初始化信息结束
    #
    #     # 必须是我加入的频道
    #     if self.room_channel_no in self.request_user.profile.get_my_chat_room():
    #         # 加入成员保存字典 redis缓存中
    #         ChatCache(self.room_group_name).set_add(self.profile_uid)
    #         # 打印信息
    #         print('UID:%s加入房间(%s),剩余:%s' % (
    #             self.profile_uid, self.room_group_name,
    #             ChatCache(self.room_group_name).set_members()))
    #         # Join room group
    #         await self.channel_layer.group_add(
    #             self.room_group_name,
    #             self.channel_name
    #         )
    #         await self.accept()
    #     # 机器人回复频道
    #     elif self.room_type == 'ROBOT':
    #         # Join room group
    #         await self.channel_layer.group_add(
    #             self.room_group_name,
    #             self.channel_name
    #         )
    #         await self.accept()
    #     else:
    #         await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 初始化房间信息
    async def action_first_init(self):
        # 我加入的房间信息
        now = datetime.now()
        my_join_room = ChatRoom.objects.filter(
            Q(admins__user=self.request_user) | Q(members__user=self.request_user)).distinct()
        room_info = ListChatRoomSerializers(my_join_room, many=True,
                                            context={'request_user': self.request_user}).data
        user_info = FriendsSerializers2(self.request_user.profile).data
        extra_data = {
            'user_info': user_info,
            'room_info': room_info
        }
        self.chaos.data.update(
            {
                'type': 'chat_message',
                'message': '初始化房间信息',
                'send_time': now.strftime('%p %H:%M'),
                'extra_data': extra_data,
            }
        )
        await self.channel_layer.group_send(self.room_group_name, self.chaos.data)

    # 群组聊天
    async def action_chat_message(self):
        now = datetime.now()
        room_orm = ChatRoom.objects.filter(channel_no=self.chaos.channel_no).first()
        room_type = room_orm.chat_type if room_orm else 'ERROR'
        if room_type == 'ROBOT':
            robot_msg, msg_type = talk_with_me(self.chaos.message)
            robot_user, _ = User.objects.get_or_create(username='robot')
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
            if self.chaos.message:
                # 与机器人聊天记录
                ChatLog.objects.create(chat_datetime=now,
                                       content=self.chaos.message,
                                       msg_type=msg_type,
                                       who_said=self.request_user,
                                       said_to_id=self.request_user.id,
                                       said_to_room=room_orm)

                ChatLog.objects.create(chat_datetime=now,
                                       content=robot_msg,
                                       msg_type=msg_type,
                                       who_said=robot_user,
                                       said_to_id=self.request_user.id,
                                       said_to_room=room_orm)
        elif room_type == 'COMMON':
            self.chaos.data.update(
                {
                    'type': 'chat_message',
                    'send_time': now.strftime('%p %H:%M'),
                    'user_uid': self.user_uid,
                }
            )
            await self.channel_layer.group_send(self.room_group_name, self.chaos.data)

            # if self.chaos.message:
            # queryset = []
            # for on in online_list:
            #     queryset.append(ChatLog(chat_datetime=now,
            #                             content=message,
            #                             msg_type=chaos.msg_type,
            #                             who_said=self.request_user,
            #                             said_to=User.objects.filter(profile__unicode_id=on).first(),
            #                             said_to_room=room_orm,
            #                             status='read'))
            # for out in outline_list:
            #     queryset.append(ChatLog(chat_datetime=now,
            #                             content=message,
            #                             msg_type=chaos.msg_type,
            #                             who_said=self.request_user,
            #                             said_to=User.objects.filter(profile__unicode_id=out).first(),
            #                             said_to_room=room_orm,
            #                             status='unread'))
            # ChatLog.objects.bulk_create(queryset)

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
        # elif msg_type == 'chat_music':
        #     now_song_id = chaos.now_song_id
        #     action = chaos.action
        #     aplayer_data = []
        #     if 'init_data' in message:
        #         aplayer_data = MusicRobot().get_now_song_data_list()
        #         action = 'init_data'
        #         # 询问其他人进度
        #     elif '点歌' in message:
        #         message = message.replace('点歌', '', 1).strip()
        #         song_info = MusicRobot().pick_a_song(message)
        #         # 找不到歌曲，或歌曲已存在
        #         if not song_info:
        #             action = 'tips'
        #         else:
        #             aplayer_data = [song_info]
        #             action = 'add_song'
        #     elif "切歌" in message:
        #         MusicRobot().switch_next_song(now_song_id)
        #         action = 'switch_next_song'
        #     elif action == 'reload_song_url':
        #         music_robot = MusicRobot()
        #         music_robot.del_song_data(now_song_id)
        #         new_song_url = music_robot.get_song_url(now_song_id)
        #         if not new_song_url:
        #             action = 'tips'
        #         else:
        #             message['url'] = new_song_url
        #             music_robot.upload_song_data(now_song_id, message)
        #             aplayer_data = [message]
        #     elif action == 'remove_song':
        #         MusicRobot().del_song_data(now_song_id)
        #         return
        #     elif action == 'ack_song_process':
        #         print('询问其他人播放进度')
        #     elif action == 'syn_song_process':
        #         print('回答自己歌曲播放进度', self.request_user.profile.nick_name, message)
        #         # todo 改为自己的 return
        #         if float(message) < 1:
        #             return
        #         aplayer_data = message
        #     elif action == 'quit_listen_song':
        #         print(message)
        #     elif action == 'update_song':
        #         MusicRobot().update_song_data_song_process(now_song_id, 'song_process', message)
        #         return
        #     else:
        #         msg_type = 'chat_message'
        #         aplayer_data = message
        #     print('>>>当前歌单\n', aplayer_data)
        #     await self.channel_layer.group_send(
        #         self.room_group_name,
        #         {
        #             'type': 'chat_message',
        #             'message': aplayer_data,
        #             'msg_type': msg_type,
        #             'user_id': str(self.request_user.id),
        #             'send_time': '',
        #             'action': action,
        #             'song_index': chaos.song_index,
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
