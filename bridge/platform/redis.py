from pydantic import BaseModel

from bridge.platform.base import Platform


class RedisEnvironment(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


def build_redis_environment(platform: Platform) -> RedisEnvironment:
    if platform == Platform.LOCAL:
        return RedisEnvironment()
    elif platform == Platform.RENDER:
        from bridge.platform.render import build_render_redis_environment

        return build_render_redis_environment()
    else:
        raise NotImplementedError(f"Unsupported platform for Redis: {platform}")
