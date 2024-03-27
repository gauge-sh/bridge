import sys
from typing import Optional

import docker
from abc import ABC, abstractmethod

from pydantic import BaseModel


def get_docker_client() -> docker.DockerClient:
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        print("❌ Bridge Error: Make sure docker is installed and running.")
        sys.exit(1)

    return client


class ContainerConfig(BaseModel):
    """
    Container configuration information.

    All of the data needed to start a container. Matches the method signature of `docker.container.create()`
    """

    image: str
    name: str
    ports: dict = {}
    volumes: dict = {}
    restart_policy: dict = {"Name": "always"}
    environment: dict | BaseModel = {}


class DockerService(ABC):
    def __init__(self, client: docker.DockerClient, config: ContainerConfig) -> None:
        self.client = client
        self.config = config
        # todo add self.container - should we start or fetch the container on startup?

    def start(self):
        self.pull_image()
        self.start_container()
        self.ensure_ready()

    def pull_image(self):
        if not self.client.images.list(name=self.config.image):
            print(f"Image {self.config.image} not found. Pulling...")
            self.client.images.pull(self.config.image)
            print("Image pulled successfully.")

    def start_container(self):
        self.pull_image()
        containers = self.client.containers.list(
            filters={"name": self.config.name}, all=True
        )
        if containers:
            # Container names are unique, there are 1 or 0 results
            [container] = containers
            if container.status in ["paused", "exited"]:
                print(
                    f"Container {self.config.name} in bad state ({container.status}), restarting..."
                )
                container.restart()
            else:
                print(f"Container {self.config.name} already running.")
        else:
            print(f"Creating and starting container {self.config.name}...")
            self.client.containers.run(
                **self.config.dict(),
                detach=True,
            )
            print(f"Container {self.config.name} created and started.")

    @abstractmethod
    def ensure_ready(self) -> None: ...
