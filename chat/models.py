from datetime import datetime
from itertools import chain

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from dj_chat.settings import MOREN_TOUXIANG, QUNZU_TOUXIANG


class ChatRoom(models.Model):
    CHAT_TYPE = (
        ('COMMON', '普通类型'),
        ('MUSIC', '音乐类型'),
        ('ROBOT', '机器人回复'),
    )
    room_name = models.CharField(max_length=64, null=False, blank=False, help_text='房间名称')
    room_description = models.CharField(max_length=255, default='这里还没什么描述', help_text='房间描述')
    img_path = models.CharField(max_length=255, default=QUNZU_TOUXIANG, help_text='头像地址')
    channel_no = models.CharField(max_length=8, null=False, blank=False, unique=True, help_text='房间频道号')
    admins = models.ManyToManyField('UserProfile', related_name='chat_admins', help_text='房间管理')
    members = models.ManyToManyField('UserProfile', related_name='chat_member', help_text='房间成员')
    max_number = models.IntegerField(default=5, help_text='允许最大人数')
    ordering = models.IntegerField(default=99, help_text='置顶权')
    chat_type = models.CharField(default='COMMON', choices=CHAT_TYPE, help_text='房间类型', max_length=16)
    date_created = models.DateTimeField(default=datetime.now)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.room_name

    class Meta:
        verbose_name = "聊天室"
        verbose_name_plural = verbose_name

    def get_members_unicode_id(self):
        """
        该房间管理员和成员的uid列表
        :return: list[str]
        """
        member_list = list(self.members.values_list('unicode_id', flat=True))
        admin_list = list(self.admins.values_list('unicode_id', flat=True))
        return member_list + admin_list

    def get_members(self):
        """
        该房间管理员和成员的queryset
        :return: Queryset
        """
        member_list = self.members.all()
        admin_list = self.admins.all()
        return chain(member_list, admin_list)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nick_name = models.CharField(max_length=64, help_text='昵称')
    signature = models.CharField(max_length=255, null=True, blank=True, help_text='个性签名')
    friends = models.ManyToManyField('self', related_name='my_friends', blank=True)
    unicode_id = models.IntegerField(default=-1, blank=False, null=False, unique=True, help_text='唯一ID')
    img_path = models.CharField(max_length=255, default=MOREN_TOUXIANG, help_text='头像地址')
    city = models.CharField(max_length=64, help_text='城市', null=True, blank=True)
    qq_number = models.CharField(max_length=16, help_text='qq号码', null=True, blank=True)
    is_use_qq_img = models.BooleanField(default=False, help_text='是否使用QQ头像')

    date_created = models.DateTimeField(default=datetime.now)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nick_name + ': ' + str(self.unicode_id)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def get_img_path(self):
        img_path = self.img_path
        if self.is_use_qq_img and self.qq_number:
            img_path = 'http://q1.qlogo.cn/g?b=qq&nk=%s&s=100' % (self.qq_number)
        elif img_path == '/':
            img_path = MOREN_TOUXIANG
        return img_path

    def get_my_chat_room(self):
        """
        我加入的房间列表
        :return: list[str]
        """
        chat_member = self.chat_member.all().values_list('channel_no', flat=True)
        chat_admins = self.chat_admins.all().values_list('channel_no', flat=True)
        return list(chat_member) + list(chat_admins)


class ChatLog(models.Model):
    chat_datetime = models.DateTimeField(null=True, blank=True, db_index=True, help_text='接收时间')
    content = models.TextField(null=True, blank=True, help_text='聊天内容')
    msg_type = models.CharField(max_length=16, null=True, blank=True, help_text='消息类型')
    who_said = models.ForeignKey(User, on_delete=models.CASCADE, db_constraint=False, related_name='who_said',
                                 help_text='发送者')
    said_to = models.ForeignKey(User, on_delete=models.CASCADE, db_constraint=False, null=True, blank=True,
                                related_name='said_to', help_text='接收者')
    said_to_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, db_constraint=False, null=True, blank=True,
                                     related_name='said_to_room', help_text='接收房间')
    said_together = models.CharField(max_length=64, null=True, blank=True)
    status = models.CharField(max_length=16, default='read', help_text='消息状态')

    class Meta:
        verbose_name = "聊天记录"
        verbose_name_plural = verbose_name


class TalkLog(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, db_constraint=False, related_name='talk_log',
                                help_text='说说')
    content = models.TextField(null=True, blank=True, help_text='说说内容')
    star = models.IntegerField(default=0)
    reading = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=datetime.now)
    date_modified = models.DateTimeField(auto_now=True)


class History(models.Model):
    ip = models.CharField(max_length=64, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)
    device = models.CharField(max_length=64, null=True, blank=True)
    count = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=datetime.now)
