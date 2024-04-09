from bridge.platform.base import Platform
from bridge.platform.render import build_render_redis_environment
from bridge.service.redis import RedisEnvironment


def build_redis_environment(platform: Platform) -> RedisEnvironment:
    if platform == Platform.LOCAL:
        return RedisEnvironment()
    elif platform == Platform.RENDER:
        return build_render_redis_environment()
    else:
        raise ValueError(f"Unsupported platform for Redis: {platform}")
