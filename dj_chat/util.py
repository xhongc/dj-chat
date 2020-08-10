from collections import defaultdict

from django.core.cache import cache


class ChatCache(object):
    def __init__(self, name):
        self.redis_client = cache.get_client(1)
        self.name = name

    # ## 集合 ###
    def set_add(self, *args):
        """Set sadd 添加元素到集合中"""
        self.redis_client.sadd(self.name, *args)

    def set_len(self):
        """ 返回集合中元素的个数"""
        return self.redis_client.scard(self.name)

    def set_members(self):
        """获取集合中的所有元素"""
        return self.redis_client.smembers(self.name)

    def set_is_member(self, value):
        """判断某个值是否在集合中"""
        return self.redis_client.sismember(self.name, value)

    def set_remove(self, *args):
        """删除集合中的一个或多个元素"""
        self.redis_client.srem(self.name, *args)

    # ## 列表 ###
    def list_rpush(self, *args):
        """value值有多个时，从左到右依次向列表右边添加，类型可以不同"""
        self.redis_client.rpush(self.name, *args)

    def list_len(self):
        """获取所给键的列表大小"""
        return self.redis_client.llen(self.name)

    def list_set(self, index, value):
        """ lset 列表中通过索引赋值"""
        self.redis_client.lset(self.name, index, value)

    def list_index(self, index):
        """ lindex 通过索引获取列表值"""
        self.redis_client.lindex(self.name, index)

    def list_lpop(self):
        """lpop 删除左边的第一个值并返回"""
        return self.redis_client.lpop(self.name)

    def list_remove(self, start=0, end=-1):
        """删除非start到end"""
        self.redis_client.ltrim(self.name, start, end)

    def list_all(self):
        """返回所有类别"""
        return self.redis_client.lrange(self.name, 0, -1)

    # ##Hash map###
    def hash_set(self, key, value):
        self.redis_client.hset(self.name, key, value)

    def hash_mset(self, mapping):
        """设置哈希中的多个键值对"""
        self.redis_client.hmset(self.name, mapping)

    def hash_hget(self, key):
        return self.redis_client.hget(self.name, key)

    def hash_getall(self):
        """
        Hash hgetall 获取哈希中所有的键值对
        :return type dict
        """
        return self.redis_client.hgetall(self.name)

    def hash_keys(self):
        """ 获取哈希中所有的键key"""
        return self.redis_client.hkeys(self.name)

    def hash_len(self):
        return self.redis_client.hlen(self.name)

    def hash_values(self):
        """hvals 获取哈希中所有的值value"""
        return self.redis_client.hvals(self.name)

    def hash_exists(self, key):
        return self.redis_client.hexists(self.name, key)

    def hash_del(self, *keys):
        self.redis_client.hdel(self.name, *keys)


if __name__ == '__main__':
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj_chat.settings")
    ca = ChatCache('musiclist')
    print(ca.hash_keys())
    ca.hash_del(*ca.hash_keys())

    print(ca)
