import sys
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast

import docker
from docker.models.containers import Container
from pydantic import BaseModel, Extra, Field
from rich.console import Console

from bridge.console import log_error, log_task

if TYPE_CHECKING:
    import docker.errors


def get_docker_client() -> docker.DockerClient:
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        log_error("Make sure docker is installed and running")
        sys.exit(1)

    return client


class BaseEnvironment(BaseModel):
    def to_container_run_kwargs(self) -> dict[str, Any]:
        return self.model_dump()

    class Config:
        extra = Extra.allow


T_Environment = TypeVar("T_Environment", bound=BaseEnvironment)


class ContainerConfig(BaseModel, Generic[T_Environment]):
    """
    Container configuration information.

    All the data needed to start a container.
    """

    image: str
    name: str
    ports: dict[str, int] = Field(default_factory=dict)
    volumes: dict[str, str] = Field(default_factory=dict)
    restart_policy: dict[str, str] = {"Name": "always"}
    environment: T_Environment = BaseEnvironment()

    def to_container_run_kwargs(self) -> dict[str, Any]:
        # Right now the above spec matches `docker.container.run`, model_dump is sufficient
        dict_rep = self.model_dump()
        dict_rep["environment"] = self.environment.to_container_run_kwargs()
        return dict_rep


T_ContainerConfig = TypeVar("T_ContainerConfig", bound=ContainerConfig)


class DockerService(ABC, Generic[T_ContainerConfig]):
    def __init__(self, client: docker.DockerClient, config: T_ContainerConfig) -> None:
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
                [model] = containers
                container = cast(Container, model)
                if container.status in ["paused", "exited"]:
                    container.restart()
            else:
                self.client.containers.run(
                    **self.config.to_container_run_kwargs(),
                    detach=True,
                )

    @abstractmethod
    def ensure_ready(self) -> None: ...
