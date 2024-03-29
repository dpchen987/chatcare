import time


class MemCacheList:
    def __init__(self, max_length=10):
        self.cache = {}
        self.max_length = max_length

    def save(self, chat_id, message):
        if chat_id in self.cache:
            self.cache[chat_id].append(message)
        else:
            self.cache[chat_id] = [message]
        while len(self.cache[chat_id]) > self.max_length:
            self.cache[chat_id].pop(0)

    def get(self, chat_id):
        if chat_id not in self.cache:
            self.cache[chat_id] = []
        cachelist = self.cache.get(chat_id)
        while len(cachelist) > self.max_length:
            cachelist.pop(0)
        return cachelist

    def remove(self, chat_id):
        if chat_id in self.cache:
            self.cache.pop(chat_id)


class MemCache:
    '''
    cache chat context in memory
    '''

    def __init__(self, expire=180):
        self.cache = {}  # {chat_id: {intent_id: xxx, entities: [], time: xxx}}
        self.expire = expire
        self.clear_last = time.time()
        self.clear_gap = 3600  # clear expired cache every 1 hour

    def save(self, chat_id, intent_id, entities):
        self.cache[chat_id] = {
            'intent_id': intent_id,
            'entities': entities,
            'time': time.time()
        }

    def get(self, chat_id):
        if time.time() - self.clear_last > self.clear_gap:
            self.clear_last = time.time()
            self.clear()
        cache = self.cache.get(chat_id)
        if cache and time.time() - cache['time'] > self.expire:
            self.cache.pop(chat_id)
            cache = None
        return cache

    def remove(self, chat_id):
        if chat_id in self.cache:
            self.cache.pop(chat_id)

    def clear(self,):
        now = time.time()
        to_delete = []
        for k, v in self.cache.items():
            past = now - v['time']
            if past > self.expire:
                to_delete.append(k)
        for k in to_delete:
            self.cache.pop(k)


class RedisCache:
    '''
    cache chat context in Redis
    '''
    import redis
    import json

    def __init__(self, host, port, expire=180):
        self.r = self.redis.Redis(host=host, port=port, decode_responses=True)
        self.expire = expire

    def save(self, chat_id, intent_id, entities):
        oo = {
            'intent_id': intent_id,
            'entities': entities
        }
        js = self.json.dumps(oo)
        self.r.set(chat_id, js, ex=self.expire)

    def get(self, chat_id):
        js = self.r.get(chat_id)
        if not js:
            return None
        oo = self.json.loads(js)
        return oo


if __name__ == '__main__':
    rc = RedisCache('localhost', 6379)
    rc.save('12345', 'test', [])
