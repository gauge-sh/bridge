from time import sleep

import docker
import redis

from bridge.console import log_task
from bridge.service.docker import ContainerConfig, DockerService


class RedisConfig(ContainerConfig):
    image: str = "redis:7.2.4"
    name: str = "bridge_redis"
    ports: dict = {"6379/tcp": 6379}


class RedisService(DockerService):
    def __init__(self, client: docker.DockerClient, config: RedisConfig) -> None:
        super().__init__(client, config)

    def ensure_ready(self):
        with log_task(
            start_message=f"Waiting for [white]{self.config.name}[/white] to be ready",
            end_message=f"[white]{self.config.name}[/white] is ready",
        ):
            while True:
                try:
                    # Attempt to create a connection to Redis
                    r = redis.Redis(
                        host="localhost", port=self.config.ports["6379/tcp"]
                    )
                    if r.ping():
                        return  # Redis is ready and responding
                except redis.ConnectionError:
                    sleep(0.1)
