from abc import ABC, abstractmethod

import docker

from bridge.service.postgres import PostgresConfig, PostgresService


class FrameWorkHandler(ABC):
    def __init__(self, framework_locals: dict, enable_postgres: bool):
        self.framework_locals = framework_locals
        self.enable_postgres = enable_postgres

    def run(self) -> None:
        """Start services."""
        client = docker.from_env()
        if self.enable_postgres:
            self.start_postgres(client)

    def start_postgres(self, client: docker.DockerClient) -> None:
        config = PostgresConfig()
        service = PostgresService(client=client, config=config)
        service.start()
        self.configure_postgres(config)

    @abstractmethod
    def configure_postgres(self, config: PostgresConfig) -> None:
        """Update framework_locals with the correct configuration for postgres"""
        pass

    # TODO teardown?
    # TODO generalize each service?
