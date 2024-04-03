import sys
from abc import ABC, abstractmethod

import docker
from pydantic import BaseModel
from rich.console import Console

from bridge.console import log_error, log_task


def get_docker_client() -> docker.DockerClient:
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        log_error("Make sure docker is installed and running")
        sys.exit(1)

    return client


class ContainerConfig(BaseModel):
    """
    Container configuration information.

    All of the data needed to start a container.
    Matches the method signature of `docker.container.create()`
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
        console = Console()
        console.print(
            f"[bold bright_green]Setting up service "
            f"[white]{self.config.name}[/white]..."
        )
        self.pull_image()
        self.start_container()
        self.ensure_ready()
        console.print(
            f"[bold bright_green]Service [white]{self.config.name}[/white] started!"
        )

    def pull_image(self):
        with log_task(
            start_message=f"Pulling [white]{self.config.image}",
            end_message=f"Image [white]{self.config.image}[/white] pulled",
        ):
            if not self.client.images.list(name=self.config.image):
                self.client.images.pull(self.config.image)

    def start_container(self):
        with log_task(
            start_message=f"Starting container [white]{self.config.name}[/white]",
            end_message=f"Container [white]{self.config.name}[/white] started",
        ):
            containers = self.client.containers.list(
                filters={"name": self.config.name}, all=True
            )
            if containers:
                # Container names are unique, there are 1 or 0 results
                [container] = containers
                if container.status in ["paused", "exited"]:
                    container.restart()
            else:
                self.client.containers.run(
                    **self.config.dict(),
                    detach=True,
                )

    @abstractmethod
    def ensure_ready(self) -> None: ...
