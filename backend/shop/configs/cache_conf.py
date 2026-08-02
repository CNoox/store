from dotenv import load_dotenv
import os
load_dotenv()

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_LOCATION'),
    }
}
CACHE_TTL = 60*15