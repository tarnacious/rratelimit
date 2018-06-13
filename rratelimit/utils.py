import os

from .exceptions import UnsupportedRedisVersion

basepath = os.path.abspath(os.path.dirname(__file__))


class AbstractLimiter(object):

    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def get_key(self, actor):
        return ':'.join(['rratelimit', self.action, actor])

    def alert(self, *args, **kwargs):
        raise NotImplementedError

    def exceeded(self, *args, **kwargs):
        raise NotImplementedError

    def clear(self, *args, **kwargs):
        raise NotImplementedError


class LuaLimiter(AbstractLimiter):

    async def setup(self):
        await self.check_ver()
        await self.register_all()

    async def register_script(self, redis, scriptname):
        """Register script located at ./lua/<scriptname>.lua"""
        path = os.path.join(basepath, 'lua', scriptname+'.lua')
        script = await redis.script_load(open(path).read())

        async def exec_script(keys=[], args=[], client=None):
            return await self.redis.evalsha(script, keys=keys, args=args)

        return exec_script

    def register_all(self, *args, **kwargs):
        """Registers all lua scripts on redis instance'
           Must be overridden by child."""
        raise NotImplementedError

    async def check_ver(self):
        def versiontuple(v):
            return tuple(map(int, (v.split("."))))

        info = await self.redis.info()
        version = info['server']['redis_version']
        if versiontuple(version) < versiontuple("2.6.0"):
            raise UnsupportedRedisVersion(version)


def dtime(timestamp, slots, period):
    """ Discrete time.

    Takes time and converts into into
    discrete cyclical blocks."""
    return int(timestamp / period) % slots
