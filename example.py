import rratelimit
import asyncio
import aioredis
from rratelimit import Limiter

loop = asyncio.get_event_loop()

async def go():
    redis = await aioredis.create_redis_pool('redis://localhost')
    key = "user_x_bla"
    limit = 2
    period = 3
    limiter = Limiter(redis, action=key, limit=limit, period=period)
    await limiter.setup()
    for _ in range(5):
        print(await limiter.checked_insert(key))

loop.run_until_complete(go())

