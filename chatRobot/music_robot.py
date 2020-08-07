from chatRobot.neteaseApi.netEasemusic import NetEaseServer


class MusicRobot(object):
    def __init__(self):
        self.nes = NetEaseServer()
        self.aplayer_data = {
            'name': '',
            'artist': '',
            'url': '',
            'cover': '',  # 唱片图片
            'lrc': '',
            'theme': '#ebd0c2'
        }

    def _get_song_id(self, keyword):
        return self.nes.get_song_id(keyword=keyword)

    def get_song_url(self, song_id):
        return self.nes.get_song_url(song_id=song_id)

    def _get_song_lyric(self, song_id):
        return self.nes.get_song_lyric(song_id=song_id)

    def _get_song_detail(self, song_id):
        return self.nes.get_song_details(song_id=song_id)

    def get_song_info(self, keyword):
        song_id = self._get_song_id(keyword=keyword)
        song_lyric = self._get_song_lyric(song_id=song_id)
        song_detail = self._get_song_detail(song_id=song_id)
        song_url = self.get_song_url(song_id=song_id)
        self.aplayer_data['name'] = song_detail['name']
        self.aplayer_data['artist'] = song_detail['artist']
        self.aplayer_data['url'] = song_url
        self.aplayer_data['cover'] = song_detail['picture_url']
        self.aplayer_data['lrc'] = song_lyric
        return self.aplayer_data
