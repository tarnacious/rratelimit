import rratelimit
import asyncio
import aioredis
from rratelimit import Limiter

loop = asyncio.get_event_loop()

async def get_pool():
    return await aioredis.create_redis_pool(
        'redis://localhost',
        minsize=5, maxsize=10,
        loop=loop)

pool = loop.run_until_complete(get_pool())

limit = 2
period = 3
key = 'request_{}_{}'.format(limit, period)

async def get_limiter():
    limiter =  Limiter(pool, action=key, limit=limit, period=period)
    await limiter.setup()
    return limiter

async def check_limit(limiter, key):
    return await limiter.checked_insert(key)

limiter = loop.run_until_complete(get_limiter())

for _ in range(5):
    print(loop.run_until_complete(check_limit(limiter, key)))
