from time import sleep

import docker
import redis
from pydantic import BaseModel

from bridge.console import log_task
from bridge.service.docker import ContainerConfig, DockerService


class RedisEnvironment(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}"


class RedisConfig(ContainerConfig):
    image: str = "redis:7.2.4"
    name: str = "bridge_redis"
    ports: dict = {"6379/tcp": 6379}
    environment: RedisEnvironment = RedisEnvironment()


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
                        host=self.config.environment.host,
                        port=self.config.environment.port,
                    )
                    if r.ping():
                        return  # Redis is ready and responding
                except redis.ConnectionError:
                    sleep(0.1)
