import docker

from bridge.service.redis import RedisService


def open_redis_shell():
    client = docker.from_env()
    postgres_service = RedisService(client=client)
    postgres_service.start()
    postgres_service.shell()
