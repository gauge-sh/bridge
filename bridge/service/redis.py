import os
from time import sleep
from typing import Optional

import docker
import redis

from bridge.console import log_task
from bridge.platform.redis import RedisEnvironment
from bridge.service.docker import ContainerConfig, DockerService


class RedisConfig(ContainerConfig):
    image: str = "redis:7.2.4"
    name: str = "bridge_redis"
    ports: dict[str, int] = {"6379/tcp": 6379}


class RedisService(DockerService[RedisConfig]):
    def __init__(
        self, client: docker.DockerClient, config: Optional[RedisConfig] = None
    ) -> None:
        super().__init__(client, config or RedisConfig())
        self.redis_client_environment = RedisEnvironment()

    def ensure_ready(self):
        with log_task(
            start_message=f"Waiting for [white]{self.config.name}[/white] to be ready",
            end_message=f"[white]{self.config.name}[/white] is ready",
        ):
            while True:
                try:
                    # Attempt to create a connection to Redis
                    r = redis.Redis(
                        host=self.redis_client_environment.host,
                        port=self.redis_client_environment.port,
                    )
                    if r.ping():
                        return  # Redis is ready and responding
                except redis.ConnectionError:
                    sleep(0.1)

    def shell(self):
        # Open a shell to the Redis container
        # NOTE: This entirely replaces the currently running process!
        os.execvp("docker", ["docker", "exec", "-it", self.config.name, "redis-cli"])
