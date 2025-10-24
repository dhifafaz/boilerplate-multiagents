import redis
from source.config import settings

class RedisService:
    
    instance = None
    
    def __new__(cls):
        if cls.instance is None:
            cls.instance = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True
            )
        return cls.instance