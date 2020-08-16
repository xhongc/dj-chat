class ChaosBody(object):
    """websocket消息类"""

    def __init__(self, data):
        # 必须传的元素
        assert isinstance(data, dict)
        assert 'message' in data
        assert 'channel_no' in data
        for k, v in data.items():
            setattr(self, k, v)

    @property
    def data(self):
        return self.__dict__

    def __getattr__(self, item):
        return None


if __name__ == '__main__':
    data = {
        'msg_type': 'chat_message',
        'chat_type': 'chat_message',
        'message': '123',
        'channel_no': 'GP_robot',
        'action': 'first_init'
    }
    chao = ChaosBody(data)
    chao.arm = '111221'
    print(chao.a)
