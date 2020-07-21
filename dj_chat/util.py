from collections import defaultdict

from django.core.cache import cache


class ChatCache(object):
    def __init__(self):
        if not cache.get('chats'):
            cache.set('chats', defaultdict(set))
        self.chat_cache = cache.get('chats')

    def append(self, chat_group, profile_uid):
        self.chat_cache[chat_group].add(profile_uid)
        cache.set('chats', self.chat_cache)

    def append_delay(self, chat_group, profile_uid, delay=10):
        print('add', self.chat_cache[chat_group])
        self.chat_cache[chat_group].add(profile_uid)
        cache.set('chats', self.chat_cache, delay)

    def remove(self, chat_group, profile_uid):
        self.chat_cache[chat_group].remove(profile_uid)
        cache.set('chats', self.chat_cache)

    def get_cache(self, chat_group):
        return cache.get('chats', defaultdict(set)).get(chat_group, defaultdict(set))


if __name__ == '__main__':
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj_chat.settings")

    ca = ChatCache()
    print(ca.get_cache('test'))

    # ca.append('test', 'ca-123')
    ca.append_delay('test', 'ca-124', 2)
    print(ca.get_cache('test'))
    import time

    time.sleep(3)
    print(ca.get_cache('test'))
    print(ca.get_cache('chats'))
