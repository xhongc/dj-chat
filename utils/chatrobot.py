import json

import requests

IMG_HTML = """<img src="%s">"""
BTC_HTML = """<iframe   src="https://cn.widgets.investing.com/top-cryptocurrencies?theme=darkTheme" width="1000px" height="460px"   frameborder="1/0"  name="iframe名称"     scrolling="yes/no/auto">   
</iframe>"""
GP_HTML = """<iframe   src="https://cn.widgets.investing.com/live-indices?theme=darkTheme&pairs=959206,179,166,178,27,170,1118193" width="1000px" height="460px"   frameborder="1/0"  name="iframe名称"     scrolling="yes/no/auto">   
</iframe>"""
HELP_HTML = """回复命令<br>1. /btc  可查看比特币市值<br>2. /gp 可查股票指数<br>3./ghs 神秘代码"""


def ghs():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
    }
    try:
        resp = requests.get('https://api.66mz8.com/api/rand.tbimg.php?format=json', headers=headers).json()
        if resp.get('code') == 200:
            return IMG_HTML % (resp.get('pic_url'))
    except:
        pass
    return '呵呵，你说什么我听不懂'


def talk_with_me(content):
    if content.startswith('/'):
        return i_talk(content), 'chat_html'
    else:
        return sizhi(content), 'chat_message'


def i_talk(content):
    content = content[1:].strip()
    reply = REPLY.get(content, '未找到该命令') or '未找到该命令'
    if isinstance(reply, str):
        return reply
    elif callable(reply):
        return reply()


def sizhi(content):
    url = 'https://api.ownthink.com/bot'
    data = {
        "spoken": content,
        "appid": "xiaosi",
        "userid": "charles"
    }
    try:
        resp = requests.post(url, data=data)
        resp = json.loads(resp.text)
        if resp.get('message', '') == 'success':
            return resp.get('data').get('info').get('text')
        else:
            return '你说啥呢？'
    except Exception as e:
        print(e)
        return '咱也不知道'


REPLY = {
    'btc': BTC_HTML,
    'help': HELP_HTML,
    'gp': GP_HTML,
    'ghs': ghs,
}
if __name__ == '__main__':
    print(i_talk('/btc'))
