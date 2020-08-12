import mimetypes
import re
import time
from datetime import datetime, timedelta

import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, F, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from chat.filters import ChatLogFilter, PersonalChatLogFilter, ChatRoomFilter, UserProfileFilter
from chat.models import ChatRoom, ChatLog, UserProfile, TalkLog, History
from chat.serializers import FriendsSerializers, ListFriendsSerializers, ChatRoomSerializers, \
    ListChatLogSerializers, ListChatRoomSerializers, UpdateChatRoomSerializers, FriendsSerializers2, \
    RegisterSerializers, ListTalkLogSerializers, PostTalkLogSerializers, UserInfoSerializer
from dj_chat.util import ChatCache
from utils.base_chart import get_period_expression, get_date_range
from utils.base_serializer import BasePagination
from collections import OrderedDict
from utils.relativedelta import relativedelta


@login_required(login_url='/login/')
def index(request):
    return render(request, 'chat/boot_chat.html', locals())


class StatisticViewsets(mixins.ListModelMixin, GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_user_register_table(self):
        end = datetime.now()
        start = end - relativedelta(months=12)
        period = 'monthly'
        date_range = get_date_range(period, start, end)
        user_profile = User.objects.filter(date_joined__range=(start, end)).annotate(
            filter_date=get_period_expression(period, 'date_joined')).values('id', 'filter_date')
        res = []
        init_data = OrderedDict()
        for date in date_range:
            init_data[date] = 0
        for p in user_profile:
            init_data[p['filter_date']] += 1
        lei_jia = 0
        for k, v in init_data.items():
            structure = {'y': '', 'item1': '', 'item2': ''}
            structure['y'] = k
            structure['item1'] = v
            lei_jia += v
            structure['item2'] = lei_jia - v
            res.append(structure)
        return res

    def get_daily_user_register_table(self):
        end = datetime.now()
        start = end - relativedelta(days=12)
        period = 'daily'
        date_range = get_date_range(period, start, end)
        user_profile = User.objects.filter(date_joined__range=(start, end)).annotate(
            filter_date=get_period_expression(period, 'date_joined')).values('id', 'filter_date')
        res = []
        init_data = OrderedDict()
        for date in date_range:
            init_data[date] = 0
        for p in user_profile:
            init_data[p['filter_date']] += 1
        for k, v in init_data.items():
            structure = {'y': '', 'item1': ''}
            structure['y'] = k
            structure['item1'] = v
            res.append(structure)
        return res

    def get_chatroom_table(self):
        end = datetime.now()
        start = end - relativedelta(months=6)
        period = 'monthly'
        date_range = get_date_range(period, start, end)
        init_data = OrderedDict()
        res = []
        for date in date_range:
            init_data[date] = 0
        chat_room = ChatRoom.objects.filter(date_created__range=(start, end)).annotate(
            filter_date=get_period_expression(period, 'date_created')).values('id', 'filter_date')
        for p in chat_room:
            init_data[p['filter_date']] += 1
        lei_jia = 0
        for k, v in init_data.items():
            structure = {'y': '', 'a': '', 'b': ''}
            structure['y'] = k
            structure['a'] = v
            lei_jia += v
            structure['b'] = lei_jia
            res.append(structure)
        return res

    def list(self, request, *args, **kwargs):
        total_user = User.objects.count()
        total_room = ChatRoom.objects.count()
        total_online = ChatCache('__online').set_len() or 0
        total_history = History.objects.aggregate(total=Sum('count'))['total']
        user_register_table = self.get_user_register_table()
        daily_user_register_table = self.get_daily_user_register_table()
        chatroom_table = self.get_chatroom_table()
        donut = [
            {'label': "访问人次", 'value': total_history},
        ]
        return JsonResponse(
            {'area': user_register_table, 'bar': chatroom_table, 'donut': donut, 'line': daily_user_register_table,
             'total_user': total_user, 'total_room': total_room,
             'total_online': total_online, 'total_history': total_history}, status=200)


class RegisterViewsets(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = RegisterSerializers


class ChatIndexViewsets(mixins.ListModelMixin, GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def list(self, request, *args, **kwargs):
        return render(request, template_name='chat/boot_chat.html')


class UserProfileViewsets(mixins.ListModelMixin, GenericViewSet):
    def get_queryset(self):
        request_user = self.request.user
        queryset = UserProfile.objects.exclude(friends__user=request_user)
        return queryset

    serializer_class = FriendsSerializers2
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)


class UserInfoViewsets(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserInfoSerializer
    lookup_field = 'user'
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)


class FriendsViewsets(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = FriendsSerializers
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        channel_no = self.request.query_params.get('channel_no', None)
        if channel_no:
            return self.request.user.profile.friends.exclude(chat_member__channel_no=channel_no).exclude(
                chat_admins__channel_no=channel_no)
        return self.request.user.profile.friends.all()

    def get_serializer_class(self):
        if self.action == 'create':
            serializer_class = FriendsSerializers
        elif self.action == 'list':
            serializer_class = ListFriendsSerializers
        else:
            raise Exception('no such method')
        return serializer_class


class ChatLogViewsets(mixins.ListModelMixin, GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    pagination_class = BasePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ChatLogFilter

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return ListChatLogSerializers
        return ListChatLogSerializers

    def get_queryset(self):
        start = datetime.now().date()
        end = start + timedelta(days=1)
        return ChatLog.objects.filter(chat_datetime__range=(start, end), said_to=self.request.user).order_by(
            '-chat_datetime', '-id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 把未读变成已读
            ChatLog.objects.filter(status='unread', said_to=request.user,
                                   said_to_room__channel_no=request.query_params.get(
                                       'said_to_room__channel_no')).update(
                status='read')
            return self.get_paginated_response(serializer.data[::-1])

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PersonalChatLogViewsets(mixins.ListModelMixin, GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    pagination_class = BasePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PersonalChatLogFilter

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'list':
            return ListChatLogSerializers
        return ListChatLogSerializers

    def get_queryset(self):
        start = datetime.now().date()
        end = start + timedelta(days=1)
        return ChatLog.objects.filter(chat_datetime__range=(start, end)).order_by(
            '-chat_datetime', '-id')

    def list(self, request, *args, **kwargs):
        send_to_user_uid = request.query_params.get('who_said__profile__unicode_id')
        said_together = '&'.join(sorted([str(request.user.profile.unicode_id), send_to_user_uid]))
        queryset = self.get_queryset().filter(said_together=said_together)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 把未读变成已读
            ChatLog.objects.filter(status='unread', said_to=request.user, said_together=said_together).update(
                status='read')
            return self.get_paginated_response(serializer.data[::-1])

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ChatRoomViewsets(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin, GenericViewSet):
    """
        list:
        查看房间信息成员和创建者
        create:
        创建房间
        retrieve:
        查看特定房间号信息
        update:
        邀请好友到该房间
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ChatRoomFilter
    lookup_field = 'channel_no'

    def get_queryset(self):
        channel_no = self.request.query_params.get('channel_no', None)
        is_all = self.request.query_params.get('is_all', None)
        if channel_no:
            return ChatRoom.objects.filter(channel_no=channel_no)
        else:
            filter_q = Q(admins=self.request.user.profile) | Q(members=self.request.user.profile)
            if is_all == 'true':
                return ChatRoom.objects.exclude(filter_q).distinct().order_by('ordering')
            return ChatRoom.objects.filter(filter_q).distinct().order_by('ordering')

    def get_serializer_class(self):
        if self.action == 'list':
            return ListChatRoomSerializers
        elif self.action == 'update':
            return UpdateChatRoomSerializers
        return ChatRoomSerializers

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class TalkLogViewsets(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = TalkLog.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'list':
            return ListTalkLogSerializers
        else:
            return PostTalkLogSerializers


class HistoryViewsets(mixins.ListModelMixin, GenericViewSet):
    def list(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_FORWARDED_FOR', None):
            real_ip = request.META['HTTP_X_FORWARDED_FOR']
            regip = real_ip.split(",")[-1]
        else:
            regip = request.META.get('REMOTE_ADDR', '127.0.0.2')

        his, _ = History.objects.update_or_create(ip=regip)
        his.count = his.count + 1
        his.save()
        return JsonResponse({}, status=200)


import queue
import threading
# import cv2 as cv
import subprocess as sp


class Live(object):
    def __init__(self):
        self.frame_queue = queue.Queue()
        self.command = ""
        # 自行设置
        self.rtmpUrl = "rtmp://127.0.0.1:9000/myapp/home"
        self.camera_path = 0

    def read_frame(self):
        print("开启推流")
        cap = cv.VideoCapture(0)
        print('asda')
        # Get video information
        fps = int(cap.get(cv.CAP_PROP_FPS))
        width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

        # ffmpeg command
        self.command = ['/Users/xiehongchao/PythonProject/ffmpeg-20200729-cbb6ba2-macos64-static/bin/ffmpeg',
                        '-y',
                        '-f', 'rawvideo',
                        '-vcodec', 'rawvideo',
                        '-pix_fmt', 'bgr24',
                        '-s', "{}x{}".format(width, height),
                        '-r', str(fps),
                        '-i', '-',
                        '-c:v', 'libx264',
                        '-pix_fmt', 'yuv420p',
                        '-preset', 'ultrafast',
                        '-f', 'flv',
                        self.rtmpUrl]

        # read webcamera
        while (cap.isOpened()):
            ret, frame = cap.read()

            if not ret:
                print("Opening camera is failed")
                # 说实话这里的break应该替换为：
                # cap = cv.VideoCapture(self.camera_path)
                # 因为我这俩天遇到的项目里出现断流的毛病
                # 特别是拉取rtmp流的时候！！！！
                break

            # put frame into queue
            self.frame_queue.put(frame)

    def push_frame(self):
        # 防止多线程时 command 未被设置
        while True:
            if len(self.command) > 0:
                # 管道配置
                p = sp.Popen(self.command, stdin=sp.PIPE)
                break

        while True:
            if self.frame_queue.empty() != True:
                frame = self.frame_queue.get()
                # process frame
                # 你处理图片的代码
                # write to pipe
                try:
                    p.stdin.write(frame.tostring())
                except:
                    pass

    def run(self):
        threads = [
            threading.Thread(target=Live.read_frame, args=(self,)),
            threading.Thread(target=Live.push_frame, args=(self,))
        ]
        [thread.setDaemon(True) for thread in threads]
        [thread.start() for thread in threads]


def play_video(request):
    # 推流
    live = Live()
    live.run()
    return render(request, 'chat/video.html', {'error_message': "ii"})


import re
import os
from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse


def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
    with open(file_name, "rb") as f:
        f.seek(offset, os.SEEK_SET)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            yield data


def stream_video(request):
    """将视频文件以流媒体的方式响应"""
    # range_header = request.META.get('HTTP_RANGE', '').strip()
    range_header = 'bytes=32768-2821080/2821081'.strip()
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
    range_match = range_re.match(range_header)
    path = r'C:\Users\xhongc\Desktop\fly.mp4'
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = first_byte + 1024 * 1024 * 8  # 8M 每片,响应体最大体积
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(file_iterator(path, offset=first_byte, length=length), status=206,
                                     content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        # 不是以视频流方式的获取时，以生成器方式返回整个文件，节省内存
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp
