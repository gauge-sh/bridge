import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar, Union, cast

import docker
from docker.models.containers import Container
from pydantic import BaseModel, Field
from rich.console import Console

from bridge.console import log_error, log_task
from bridge.utils.filesystem import resolve_dot_bridge
from bridge.utils.pydantic import Empty

if TYPE_CHECKING:
    import docker.errors


def get_docker_client() -> docker.DockerClient:
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        log_error("Make sure docker is installed and running")
        sys.exit(1)

    return client


T_BaseModel = TypeVar("T_BaseModel", bound=BaseModel)


class ContainerConfig(BaseModel, Generic[T_BaseModel]):
    """
    Container configuration information.

    All the data needed to start a container.
    """

    image: str
    name: str
    ports: dict[str, int] = Field(default_factory=dict)
    volumes: dict[str, Union[list[str], dict[str, str]]] = Field(default_factory=dict)
    restart_policy: dict[str, str] = {"Name": "always"}
    environment: T_BaseModel = Field(default_factory=Empty)


T_ContainerConfig = TypeVar("T_ContainerConfig", bound=ContainerConfig)


class DockerService(ABC, Generic[T_ContainerConfig]):
    def __init__(self, client: docker.DockerClient, config: T_ContainerConfig) -> None:
        self.client = client
        self.config = config
        self.container_id = None
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
        self.register()
        console.print(
            f"[bold bright_green]Service [white]{self.config.name}[/white] started!"
        )

    def register(self):
        bridge_cid_path = resolve_dot_bridge() / "cid"
        with open(bridge_cid_path, "a") as f:
            f.write(f"{self.container_id}\n")

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
                [model] = containers
                container = cast(Container, model)
                if container.status in ["paused", "exited"]:
                    container.restart()
            else:
                container = self.client.containers.run(
                    **self.config.model_dump(),
                    detach=True,
                )
            container = cast(Container, container)
            self.container_id = container.id

    @abstractmethod
    def ensure_ready(self) -> None:
        pass
