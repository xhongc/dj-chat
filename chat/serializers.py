import json
import random

from django.contrib.auth.models import User
from rest_framework import serializers

from chat.models import UserProfile, ChatLog, ChatRoom, TalkLog


class RegisterSerializers(serializers.Serializer):
    nick_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)

    def validate_username(self, attrs):
        if User.objects.filter(username=attrs).exists():
            raise serializers.ValidationError('用户名存在')
        return attrs

    def validate_password2(self, attrs):
        password = self.initial_data.get('password')
        if attrs != password:
            raise serializers.ValidationError('两次输入密码不一致')
        return attrs

    def save(self, **kwargs):
        username = self.validated_data.get('username')
        email = self.validated_data.get('email', '') or ''
        password = self.validated_data.get('password')
        nick_name = self.validated_data.get('nick_name')
        user = User.objects.create_user(username=username, password=password, email=email)
        user.profile.nick_name = nick_name
        user.profile.save()


class FriendsSerializers(serializers.Serializer):
    uid = serializers.CharField(required=True)

    def validate_uid(self, u_id):
        request = self._context.get('request')
        friends = UserProfile.objects.filter(unicode_id=u_id).first()
        if friends and u_id != request.user.profile.unicode_id:
            request.user.profile.friends.add(friends)
            request.user.profile.save()
        else:
            raise serializers.ValidationError('添加好友不存在')
        return u_id

    def save(self, **kwargs):
        u_id = self.validated_data.get('uid')
        request = self._context.get('request')
        friends = UserProfile.objects.filter(unicode_id=u_id).first()
        if friends and u_id != request.user.profile.unicode_id:
            request.user.profile.friends.add(friends)
            request.user.profile.save()
        else:
            raise Exception('error')


class FriendsSerializers2(serializers.ModelSerializer):
    img_path = serializers.SerializerMethodField()

    def get_img_path(self, obj):
        return obj.get_img_path()

    class Meta:
        model = UserProfile
        fields = '__all__'


class UserInfoSerializer(serializers.ModelSerializer):
    unicode_id = serializers.CharField(read_only=True)
    img_path = serializers.SerializerMethodField()
    is_use_qq_img = serializers.BooleanField()

    def get_img_path(self, obj):
        return obj.get_img_path()

    def validate_is_use_qq_img(self, attrs):
        return bool(attrs)

    class Meta:
        model = UserProfile
        exclude = ('friends',)


class ListFriendsSerializers(serializers.ModelSerializer):
    unread_no = serializers.SerializerMethodField()
    img_path = serializers.SerializerMethodField()

    def get_img_path(self, obj):
        img_path = obj.img_path
        if obj.is_use_qq_img and obj.qq_number:
            img_path = 'http://q1.qlogo.cn/g?b=qq&nk=%s&s=100' % (obj.qq_number)
        return img_path

    def get_unread_no(self, obj):
        request = self._context.get('request')
        said_together = '&'.join(sorted([str(obj.unicode_id), str(request.user.profile.unicode_id)]))

        unread_no = ChatLog.objects.filter(status='unread', said_to=request.user, said_together=said_together).count()
        if not unread_no:
            unread_no = ''
        return unread_no

    class Meta:
        model = UserProfile
        fields = '__all__'


class PostChatLogSerializers(serializers.ModelSerializer):
    class Meta:
        model = ChatLog
        fields = '__all__'


class ListChatLogSerializers(serializers.ModelSerializer):
    chat_datetime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = ChatLog
        fields = ('content', 'chat_datetime', 'who_said')


class ChatRoomSerializers(serializers.ModelSerializer):
    admins = serializers.CharField(read_only=True)
    channel_no = serializers.CharField(required=False)
    members = serializers.CharField(required=False)

    class Meta:
        model = ChatRoom
        fields = '__all__'

    def save(self, **kwargs):
        request = self._context.get('request')
        members = self.validated_data.pop('members') if 'members' in self.validated_data else ''
        self.validated_data['channel_no'] = 'GP_' + str(random.randint(2, 9999))
        ct_room = ChatRoom(**self.validated_data)
        self.validated_data['members'] = members
        ct_room.save()
        ct_room.admins.add(request.user.profile)
        ct_room.save()


class ListChatRoomSerializers(serializers.ModelSerializer):
    admins = FriendsSerializers2(many=True)
    members = FriendsSerializers2(many=True)
    unread_no = serializers.SerializerMethodField()

    def get_unread_no(self, obj):
        request = self._context.get('request')
        unread_no = obj.said_to_room.filter(status='unread', said_to=request.user).count()
        if not unread_no:
            unread_no = ''
        return unread_no

    class Meta:
        model = ChatRoom
        fields = '__all__'


class UpdateChatRoomSerializers(serializers.ModelSerializer):
    members = serializers.CharField()

    class Meta:
        model = ChatRoom
        fields = ('members',)

    def validate_members(self, attrs):
        return json.loads(self.initial_data.get('members'))

    def save(self, **kwargs):
        members_id = self.validated_data.get('members')
        member_count = len(set(members_id)) + self.instance.members.count() + self.instance.admins.count()
        if member_count > self._args[0].max_number:
            raise Exception('超出最大人数')
        member_list = (UserProfile.objects.get(id=id) for id in members_id)
        self.instance.members.add(*member_list)
        self.instance.save()


class ListTalkLogSerializers(serializers.ModelSerializer):
    profile = FriendsSerializers2()

    class Meta:
        model = TalkLog
        fields = '__all__'


class PostTalkLogSerializers(serializers.ModelSerializer):
    class Meta:
        model = TalkLog
        fields = '__all__'
