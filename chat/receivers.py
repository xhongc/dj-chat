from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models import signals
import random

from chat.models import UserProfile


@receiver(signals.post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        for _ in range(10):
            u_id = random.randint(100, 999)
            if UserProfile.objects.filter(unicode_id=u_id).exists():
                continue
            else:
                break
        # todo 10次失败后 换成4位数
        UserProfile.objects.create(user=instance, nick_name=instance.username, unicode_id=u_id)
        print('信号同步创建userprofile')
