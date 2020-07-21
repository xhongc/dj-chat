from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
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
from chat.models import ChatRoom, ChatLog, UserProfile, TalkLog
from chat.serializers import FriendsSerializers, ListFriendsSerializers, ChatRoomSerializers, \
    ListChatLogSerializers, ListChatRoomSerializers, UpdateChatRoomSerializers, FriendsSerializers2, \
    RegisterSerializers, ListTalkLogSerializers, PostTalkLogSerializers, UserInfoSerializer
from dj_chat.util import ChatCache
from utils.base_chart import get_period_expression, get_date_range
from utils.base_serializer import BasePagination
from collections import OrderedDict


@login_required(login_url='/login/')
def index(request):
    return render(request, 'chat/boot_chat.html', locals())


class StatisticViewsets(mixins.ListModelMixin, GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        total_user = User.objects.count()
        total_room = ChatRoom.objects.count()
        total_online = len(ChatCache().get_cache('__online') or {})
        print(ChatCache().get_cache('__online'))
        start = datetime(2020, 1, 1)
        end = datetime(2020, 8, 1)
        period = 'monthly'
        date_range = get_date_range(period, start, end)
        user_profile = User.objects.filter(date_joined__range=(start, end)).annotate(
            filter_date=get_period_expression('monthly', 'date_joined')).values('id', 'filter_date')
        res = []
        init_data = OrderedDict()
        for date in date_range:
            init_data[date] = 0
        print(user_profile.query)
        for p in user_profile:
            init_data[p['filter_date']] += 1
        print(list(user_profile))
        print(init_data)
        lei_jia = 0
        for k, v in init_data.items():
            structure = {'y': '', 'item1': '', 'item2': ''}
            structure['y'] = k
            structure['item1'] = v
            lei_jia += v
            structure['item2'] = lei_jia - v
            res.append(structure)
        print(res)
        chat_res = []
        init_data = OrderedDict()
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
            chat_res.append(structure)
        print(chat_res)

        donut = [
            {'label': "Android Site", 'value': 12},
            {'label': "PC Site", 'value': 30},
            {'label': "IOS Site", 'value': 20}
        ]
        return JsonResponse(
            {'area': res, 'bar': chat_res, 'donut': donut, 'total_user': total_user, 'total_room': total_room,
             'total_online': total_online}, status=200)


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
