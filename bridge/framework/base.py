import os
from abc import ABC, abstractmethod

import docker

from bridge.service.postgres import PostgresConfig, PostgresEnvironment, PostgresService


class FrameWorkHandler(ABC):
    def __init__(
        self, project_name: str, framework_locals: dict, enable_postgres: bool
    ):
        self.project_name = project_name
        self.framework_locals = framework_locals
        self.enable_postgres = enable_postgres

    def run(self) -> None:
        """Start services."""
        if os.environ.get("IS_BRIDGE_PLATFORM"):
            self.remote()
        else:
            client = docker.from_env()
            if self.enable_postgres:
                self.start_postgres(client)

    def remote(self) -> None:
        """Connect to remote services."""
        if self.enable_postgres:
            environment = PostgresEnvironment(
                POSTGRES_USER=os.environ["BRIDGE_POSTGRES_USER"],
                POSTGRES_PASSWORD=os.environ["BRIDGE_POSTGRES_PASSWORD"],
                POSTGRES_DB=os.environ["BRIDGE_POSTGRES_DB"],
                POSTGRES_HOST=os.environ["BRIDGE_POSTGRES_HOST"],
                POSTGRES_PORT=os.environ["BRIDGE_POSTGRES_PORT"],
            )
            self.configure_postgres(environment)

    def local(self) -> None:
        """Start services."""
        client = docker.from_env()
        if self.enable_postgres:
            self.start_postgres(client)

    def start_postgres(self, client: docker.DockerClient) -> None:
        config = PostgresConfig()
        service = PostgresService(client=client, config=config)
        service.start()
        self.configure_postgres(config.environment)

    @abstractmethod
    def configure_postgres(self, environment: PostgresEnvironment) -> None:
        """Update framework_locals with the correct configuration for postgres"""
        pass

    # TODO teardown?
    # TODO generalize each service?
