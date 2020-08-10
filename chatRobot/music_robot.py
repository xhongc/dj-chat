import json

from chatRobot.neteaseApi.netEasemusic import NetEaseServer
from django.core.cache import cache

from dj_chat.util import ChatCache


class MusicRobot(object):
    def __init__(self):
        self.nes = NetEaseServer()
        self.aplayer_data = {
            'name': '',
            'artist': '',
            'url': '',
            'cover': '',  # 唱片图片
            'lrc': '',
            'theme': '#ebd0c2',
            'song_process': '0',  # 歌曲播放进度
        }
        self.name = 'musiclist'
        self.ap_cache = ChatCache(self.name)

    def _get_song_id(self, keyword):
        return self.nes.get_song_id(keyword=keyword)

    def get_song_url(self, song_id):
        return self.nes.get_song_url(song_id=song_id)

    def _get_song_lyric(self, song_id):
        return self.nes.get_song_lyric(song_id=song_id)

    def _get_song_detail(self, song_id):
        return self.nes.get_song_details(song_id=song_id)

    def pick_a_song(self, keyword):
        """
        Step1 歌曲已经在歌单
        Step2 渠道请求歌单
        Step3 更新歌单
        :param keyword:
        :return:
        """
        song_id = self._get_song_id(keyword=keyword)
        is_exist = self.ap_cache.hash_exists(song_id)
        if is_exist:
            # 歌曲已经在歌单
            return None
        else:
            aplayer_data = self.get_song_info_and_upload(song_id)
        return aplayer_data

    def switch_next_song(self, now_song_id):
        self.ap_cache.hash_del(now_song_id)

    def get_song_info_and_upload(self, song_id):
        song_lyric = self._get_song_lyric(song_id=song_id)
        song_detail = self._get_song_detail(song_id=song_id)
        song_url = self.get_song_url(song_id=song_id)
        if not song_url: return None # 歌曲url 为none
        self.aplayer_data['id'] = song_id
        self.aplayer_data['name'] = song_detail['name']
        self.aplayer_data['artist'] = song_detail['artist']
        self.aplayer_data['url'] = song_url
        self.aplayer_data['cover'] = song_detail['picture_url']
        self.aplayer_data['lrc'] = song_lyric

        self.upload_song_data(song_id, self.aplayer_data)
        return self.aplayer_data

    def upload_song_data(self, song_id, data):
        """上传到redis"""
        self.ap_cache.hash_set(song_id, json.dumps(data))

    def get_now_song_data_list(self):
        serializer_data = [json.loads(data.decode()) for data in self.ap_cache.hash_values()]
        return serializer_data

    def del_song_data(self, song_id):
        self.ap_cache.hash_del(song_id)

    def update_song_data_song_process(self, song_id, sub_key, sub_value):
        song_dict = json.loads(self.ap_cache.hash_hget(song_id))

        song_dict[sub_key] = sub_value
        self.ap_cache.hash_set(song_id, json.dumps(song_dict))


if __name__ == '__main__':
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj_chat.settings")
    mr = MusicRobot()

    mr.update_song_data_song_process('1466792797', 'song_process', '100')
    print(mr.get_now_song_data_list())
