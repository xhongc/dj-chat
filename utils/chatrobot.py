import json

import requests


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
