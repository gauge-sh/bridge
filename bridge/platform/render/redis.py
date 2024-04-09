import os
import re

from bridge.service.redis import RedisEnvironment


def build_render_redis_environment() -> RedisEnvironment:
    # REDIS_URL contains the entire connection string, so we need to parse it
    # Regex to match the connection string components
    conn_string = os.environ.get("REDIS_URL")
    if not conn_string:
        raise ValueError("REDIS_URL environment variable must be set on Render.")
    redis_env = RedisEnvironment()
    # Optional password terminated with '@'
    # Hostname that does not contain ':' or '/'
    # Optional port number preceded by ':'
    # Optional database number preceded by '/'
    regex = (
        r"^redis:\/\/(?:(?P<password>[^@]+)@)?(?P<host>[^:\/]+)"
        r"(?::(?P<port>\d+))?(?:\/(?P<db>\d+))?$"
    )
    match = re.match(regex, conn_string)

    if match:
        components = match.groupdict()
        redis_env.host = components["host"] or "localhost"
        redis_env.port = int(components["port"] or 6379)
        redis_env.db = int(components["db"] or 0)
    else:
        raise ValueError("Invalid Redis connection string format in REDIS_URL.")

    return redis_env
