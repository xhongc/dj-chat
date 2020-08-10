import json

import requests

import chatRobot.neteaseApi.netease_encrypt as netease

BASE_URL = "http://music.163.com"
DEFAULT_TIMEOUT = 10

POST = "POST"
GET = "GET"


class NetEase(object):

    def __init__(self):
        """
        构造默认 header request session
        """
        self.header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate,sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "music.163.com",
            "Referer": "http://music.163.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
        }
        self.session = requests.session()

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
        """
        获取加密后的 form data 参数
        :param encrypt_data: 待加密的参数
        :return: 加密后的参数 {"params":"", "encSecKey":""}
        """
        key = netease.create_key(16)
        return {
            "params": netease.aes(netease.aes(encrypt_data, netease.NONCE), key),
            "encSecKey": netease.rsa(key, netease.PUBKEY, netease.MODULUS)
        }

    def request(self, method, path, data=None, default=None):
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

        url = "{}{}".format(BASE_URL, path)
        response = default
        csrf_token = ""

        data.update({"csrf_token": csrf_token})
        params = self._get_form_data(json.dumps(data).encode('utf-8'))
        try:
            response = self._raw_request(method, url, params)
            response = response.json()
            # print('[Netease api] url: {};\nresponse data:\n {}'.format(url, response))
        except requests.exceptions.RequestException as e:
            print('[Netease api] request error: {}'.format(e))
        except ValueError as e:
            print("[Netease api] request error; Path: {}, response: {}".format(path, response.text[:200]))
        finally:
            return response

    def songs_url(self, song_id):
        """
        获取音乐的实际 url，外链
            {ids: "[514235010]", level: "standard", encodeType: "aac", csrf_token: ""}
        :param song_id: 音乐 id
        :return: 带有外链的 json 串
        """
        path = "/weapi/song/enhance/player/url/v1?csrf_token="
        params = {
            'ids': '[' + str(song_id) + ']',
            'level': 'standard',
            'encodeType': 'aac',
            'csrf_token': ''
        }
        return self.request(POST, path, params)

    def songs_lyric(self, song_id):
        """
        获取音乐歌词
            {id: "186453", lv: -1, tv: -1, csrf_token: ""}
        :param song_id:
        :return:
        """
        path = "/weapi/song/lyric?csrf_token="
        params = {
            'id': str(song_id),
            'lv': -1,
            'tv': -1,
            'csrf_token': ''
        }
        return self.request(POST, path, params)

    def songs_search(self, keyword, offset=0, limit=1):
        """
        搜索音乐
            按照关键字搜索一般就用这个
            {hlpretag: "<span class="s-fc7">", hlposttag: "</span>", s: "春夏秋冬 张国荣", type: "1", offset: "0", …}
        :return:
        """
        path = '/weapi/cloudsearch/get/web?csrf_token='
        params = {
            'csrf_token': '',
            'hlposttag': '</span>',
            'hlpretag': '<span class="s-fc7">',
            'limit': str(limit),
            'offset': str(offset),
            's': str(keyword),
            'total': 'true',
            'type': '1'
        }
        return self.request(POST, path, params)

    def songs_search_(self, song):
        """
        搜索音乐，搜索框联动接口，不常用
            {s: "春夏秋冬", limit: "8", csrf_token: ""}
        :return:
        """
        path = "/weapi/search/suggest/web?csrf_token="
        params = {
            's': str(song),
            'limit': 8,
            'csrf_token': ''
        }
        return self.request(POST, path, params)

    def songs_detail(self, song_id):
        """
        获取歌曲详情
            给定 song id
            {id: "186453", c: "[{"id":"186453"}]", csrf_token: ""}
        :param song_id: 必传参数，song id
        :return: Song
        """
        path = "/weapi/v3/song/detail?csrf_token="
        params = {
            'id': str(song_id),
            'c': "[{'id': " + str(song_id) + "}]",
            'csrf_token': ''
        }
        return self.request(POST, path, params)

    def playlist_detail(self, playlist_id):
        """
        获取歌单详情
        :param playlist_id: 歌单 id
        :return: json
        """
        path = "/weapi/playlist/detail"
        params = {
            'id': str(playlist_id),
            'ids': "[" + str(playlist_id) + "]",
            'limit': 10000,
            'offset': 0,
            'csrf_token': ''
        }
        return self.request(POST, path, params)


class NetEaseServer(object):
    def __init__(self):
        self.ne = NetEase()
        self.song_details = {
            'id': '',
            'name': '',
            'artist': '',
            'url': '',
            'duration': '',
            'lyric': '',
            'picture_url': '',
            'album': '',
            'privilege': ''
        }

    def get_song_url(self, song_id):
        """
        处理返回的数据
        {'code': 200, 'data': [{'id': 1452182536, 'gain': 0.0, 'size': 3316365, 'fee': 0, 'encodeType': 'aac', 'flag': 1, 'payed': 0, 'expi': 1200, 'br': 96000, 'uf': None, 'md5': '0cb07fec649b63a516b2e05888c2c25b', 'freeTrialInfo': None, 'canExtend': False, 'url': 'http://m10.music.126.net/20200806174251/b403cda41ac723b39503386045a053ac/yyaac/obj/wonDkMOGw6XDiTHCmMOi/2717385641/eb22/182f/71ff/0cb07fec649b63a516b2e05888c2c25b.m4a', 'code': 200, 'level': 'standard', 'type': 'm4a'}]}
        """
        resp = self.ne.songs_url(song_id)
        song_url = None
        if resp.get('code') != '-1':
            song_url = resp.get('data', [{}])[0].get('url', None)
        return song_url

    def get_song_id(self, keyword, offset=0, limit=1):
        """
        处理返回的数据
        {'code': 200, 'needLogin': True, 'result': {'songCount': 17, 'highlights': ['霓虹甜心'], 'hasMore': True, 'songs': [{'m': {'vd': 18279.0, 'size': 6529581, 'br': 192000, 'fid': 0}, 'st': 0, 'h': {'vd': 15646.0, 'size': 10882605, 'br': 320000, 'fid': 0}, 'publishTime': 0, 'rtUrls': [], 'id': 1452182536, 'cf': '', 'pop': 95.0, 'mark': 128, 'ftype': 0, 'fee': 0, 'originCoverType': 2, 's_id': 0, 'mst': 9, 'alia': [], 't': 0, 'name': '霓虹甜心（翻自：马赛克）（翻自 马赛克）', 'a': None, 'rtype': 0, 'rtUrl': None, 'recommendText': None, 'cp': 0, 'alg': 'alg_search_precision_song_tab_basic', 'copyright': 0, 'officialTags': True, 'crbt': None, 'al': {'picUrl': 'http://p4.music.126.net/NoX9xOqLj6h5qYr5WAKXHw==/109951165028789740.jpg', 'pic_str': '109951165028789740', 'name': '《霓虹甜心》', 'id': 90164801, 'tns': [], 'pic': 109951165028789740}, 'privilege': {'toast': False, 'st': 0, 'id': 1452182536, 'cp': 1, 'flag': 1, 'pl': 320000, 'sp': 7, 'dl': 999000, 'fee': 0, 'payed': 0, 'subp': 1, 'cs': False, 'fl': 320000, 'maxbr': 999000}, 'rurl': None, 'noCopyrightRcmd': None, 'v': 3, 'no': 1, 'pst': 0, 'dt': 272000, 'cd': '01', 'showRecommend': False, 'l': {'vd': 19999.0, 'size': 4353069, 'br': 128000, 'fid': 0}, 'rt': '', 'djId': 0, 'mv': 0, 'ar': [{'alias': [], 'name': '小熊Una_', 'id': 34637873, 'tns': []}]}], 'rec_query': None, 'ksongInfos': {}, 'rec_type': None}}
        """
        resp = self.ne.songs_search(keyword=keyword, offset=offset, limit=limit)
        song_id = None
        if resp.get('code') != '-1':
            song_id = resp.get('result', {}).get('songs', [{}])[0].get('id', None)
        return song_id

    def get_song_id_list(self, keyword, offset=0, limit=3):
        """
        处理返回的数据列表
        """
        resp = self.ne.songs_search(keyword=keyword, offset=offset, limit=limit)
        song_id_list = []
        if resp.get('code') != '-1':
            songs = resp.get('result', {}).get('songs', [{}])
            song_id_list = [s_id.get('id', None) for s_id in songs]
        return song_id_list

    def get_song_details(self, song_id):
        resp = self.ne.songs_detail(song_id)
        if resp.get('code') != '-1':
            self.song_details['id'] = resp.get('songs', [{}])[0].get('id', None)
            self.song_details['name'] = resp.get('songs', [{}])[0].get('name', None)
            self.song_details['picture_url'] = resp.get('songs', [{}])[0].get('al', {}).get('picUrl', None)
            self.song_details['artist'] = resp.get('songs', [{}])[0].get('ar', [{}])[0].get('name', None)
        return self.song_details

    def get_song_lyric(self, song_id):
        resp = self.ne.songs_lyric(song_id)
        song_lyric = None
        if resp.get('code') != '-1':
            song_lyric = resp.get('lrc', {}).get('lyric', None)
        return song_lyric


"""
------------------------------------------------------------------------------------------------------------------------
>                                                                                                                      <
>                                                   The test case                                                      <
>                                                                                                                      <
"""


def start():
    # 1452182536
    nes = NetEaseServer()
    # a = nes.get_song_id('霓虹甜心')
    a = '1452182536'
    print(a)
    b = nes.get_song_lyric(a)
    print(b)


if __name__ == '__main__':
    start()
