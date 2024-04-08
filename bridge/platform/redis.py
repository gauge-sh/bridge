from bridge.platform.base import Platform
from bridge.service.redis import RedisEnvironment


def build_redis_environment(platform: Platform) -> RedisEnvironment:
    if platform == Platform.LOCAL:
        return RedisEnvironment()
    else:
        # TODO remote configuration
        ...
