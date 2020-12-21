import redis


class Api:

    def __init__(self):
        self.db = redis.Redis(host="redis_db", port=6379,
                              decode_responses=True)
