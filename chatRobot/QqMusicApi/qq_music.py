import base64
import json
import os
import random

import execjs
import requests

from dj_chat.settings import BASE_DIR

DEFAULT_TIMEOUT = 10

POST = "POST"
GET = "GET"
SEARCH_URL = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
MUSIC_URL = 'https://u.y.qq.com/cgi-bin/musics.fcg'
LYC_URL = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg'


class QQMusic(object):
    def __init__(self):
        self.header = {
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
            'Referer': 'https://y.qq.com/portal/singer_list.html',
        }
        self.session = requests.session()

    def get_full_params(self, param_data):
        return {
            "-": "getplaysongvkey08313544774997816",
            "g_tk": "1165295679",
            "sign": self._get_form_data(param_data),
            "loginUin": "408737515",
            "hostUin": "0",
            "format": "json",
            "inCharset": "utf8",
            "outCharset": "utf-8",
            "notice": "0",
            "platform": "yqq.json",
            "needNewCode": "0",
            "data": param_data,
        }

    def _raw_request(self, method, url, data=None):
        """
        实际发起请求方法
        :param method: POST | GET
        :param url: url
        :param data: 请求携带的数据
        :return: response
        """
        if method == "GET":
            response = self.session.get(
                url, params=data, headers=self.header, timeout=DEFAULT_TIMEOUT
            )
        elif method == "POST":
            response = self.session.post(
                url, data=data, headers=self.header, timeout=DEFAULT_TIMEOUT
            )
        else:
            raise Exception('method not allow')
        return response

    def _get_form_data(self, encrypt_data):
        filename = os.path.join(BASE_DIR, 'chatRobot/QqMusicApi/get_sgin.js')
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()

        js_data = execjs.compile(text)
        sign = js_data.call('get_sign', encrypt_data)
        return sign

    def request(self, request_url, method, data=None, default=None):
        """
        统一请求方法
        :param method: POST | GET
        :param path: 路径
        :param data: 未加密的 data
        :param default: 默认的 response
        :return: response
        """
        data = {} if not data else data
        default = {"code": -1} if not default else default

        response = default

        try:
            response = self._raw_request(method, request_url, data)
            # print('[Netease api] url: {};\nresponse data:\n {}'.format(url, response))
        except requests.exceptions.RequestException as e:
            print('[QQmusic api] request error: {}'.format(e))
        except ValueError as e:
            print("[QQmusic api] request error; response: {}".format(response.text[:200]))
        finally:
            return response

    def songs_search(self, keyword, limit=3):
        """:return <Response [200]>"""
        params = {
            'new_json': 1,
            'aggr': 1,
            'cr': 1,
            'flag_qc': 0,
            'p': 1,  # 当前页
            'n': limit,
            'w': keyword
        }
        return self.request(SEARCH_URL, GET, data=params)

    def songs_url(self, song_id):
        """
        获取音乐的实际 url，外链
        """
        random_gid = str(random.randint(1000000000, 9999999999))
        param_data = {"req": {"module": "CDN.SrfCdnDispatchServer", "method": "GetCdnDispatch",
                              "param": {"guid": random_gid, "calltype": 0, "userip": ""}},
                      "req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey",
                                "param": {"guid": random_gid, "songmid": [song_id], "songtype": [0],
                                          "uin": "0", "loginflag": 1, "platform": "20"}},
                      "comm": {"uin": "0", "format": "json", "ct": 24, "cv": 0}}
        param_data = json.dumps(param_data)

        params = self.get_full_params(param_data)
        return self.request(MUSIC_URL, GET, data=params)

    def songs_lyric(self, song_id):
        """
        获取音乐歌词
        """
        params = {
            'g_tk': '753738303',
            'songmid': song_id
        }
        return self.request(LYC_URL, GET, data=params)
        # resp = requests.get(lrc_url, headers=headers)
        # lrc_dict = json.loads(resp.text[18:-1])
        # if lrc_dict.get('lyric'):
        #     self.lyric = base64.b64decode(lrc_dict['lyric']).decode()
        # if lrc_dict.get('trans'):
        #     self.trans = base64.b64decode(lrc_dict['trans']).decode()

    def songs_detail(self, song_id):
        param_data = {"comm": {"ct": 24, "cv": 10000},
                      "albumDetail": {"module": "music.musichallAlbum.AlbumInfoServer", "method": "GetAlbumDetail",
                                      "param": {"albumMid": "004Xlk4D33fq37"}}}
        param_data = json.dumps(param_data)
        params = self.get_full_params(param_data)


class QQMUsicServer(object):
    def __init__(self):
        self.qm = QQMusic()
        self.song_details = {
            'id': '',
            'name': '',
            'artist': '',
            'url': '',
            'lrc': '',
            'cover': '',
            'theme': '#ebd0c2',
            'song_process': '0',  # 歌曲播放进度
        }

    def get_song_id_list(self, keyword, limit=1):
        """
        处理返回的数据
        """
        resp = self.qm.songs_search(keyword=keyword, limit=limit)
        resp = json.loads(resp.text[9:-1])
        # print(json.dumps(resp))
        song_id_list = []
        if resp.get('code') != '-1':
            songs = resp.get('data', {}).get('song', {}).get('list', [{}])
            song_id_list = [s_id.get('mid', None) for s_id in songs]
            self.song_details['id'] = songs[0].get('mid', None)
            self.song_details['name'] = songs[0].get('name', None)
            self.song_details['artist'] = songs[0].get('singer', [{}])[0].get('title')
            self.song_details['cover'] = \
                'https://y.gtimg.cn/music/photo_new/T002R800x800M000{albumMid}.jpg?max_age=2592000'.format(
                    albumMid=songs[0].get('album', {}).get('mid'))

        return song_id_list[0]

    def get_song_url(self, song_id):
        # 004QBfKF2rhLEC
        resp = self.qm.songs_url(song_id)
        resp = json.loads(resp.text)
        song_url = None
        if resp.get('code') != '-1':
            song_url = resp.get('req_0', {}).get('data', {}).get('midurlinfo', [{}])[0].get('purl')
            song_url = 'https://ws.stream.qqmusic.qq.com/' + song_url
            self.song_details['url'] = song_url
        return song_url


if __name__ == '__main__':
    qm = QQMUsicServer()
    print(qm.get_song_url('004QBfKF2rhLEC'))
