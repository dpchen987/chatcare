import time


class MemCache:
    '''
    cache chat context in memory
    '''

    def __init__(self, expire=180):
        self.cache = {}  # {chat_id: {intent_id: xxx, entities: [], time: xxx}}
        self.expire = expire
        self.last_clean = 0
        self.inter_clean = 3600  # clean expired cache every 1 hour

    def save(self, chat_id, intent_id, entities):
        self.cache[chat_id] = {
            'intent_id': intent_id,
            'entities': entities,
            'time': time.time()
        }

    def get(self, chat_id):
        if time.time() - self.last_clean > self.inter_clean:
            self.last_clean = time.time()
            self.clean()
        cache = self.cache.get(chat_id)
        if time.time() - cache['time'] > self.expire:
            self.cache.pop(chat_id)
            return None
        return cache

    def clean(self,):
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
