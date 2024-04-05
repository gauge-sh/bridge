import os
from abc import ABC, abstractmethod

import docker

from bridge.service.postgres import PostgresService
from bridge.platform import detect_platform, Platform


class FrameWorkHandler(ABC):
    def __init__(
        self, project_name: str, framework_locals: dict, enable_postgres: bool
    ):
        self.project_name = project_name
        self.framework_locals = framework_locals
        self.enable_postgres = enable_postgres

    def is_remote(self) -> bool:
        """
        Check if the application seems to be running on a remote platform.
        Specific frameworks may be able to detect this more accurately and should override this method.
        """
        return bool(os.environ.get("BRIDGE_PLATFORM"))

    def run(self) -> None:
        """Start services."""
        if self.is_remote():
            platform = detect_platform()
        else:
            platform = Platform.LOCAL
            self.start_local_services()
        self.configure_services(platform)

    def configure_services(self, platform: Platform) -> None:
        if self.enable_postgres:
            self.configure_postgres(platform=platform)

    def start_local_services(self):
        """Start local services if necessary"""
        client = docker.from_env()
        if self.enable_postgres:
            self.start_local_postgres(client)

    def start_local_postgres(self, client: docker.DockerClient) -> None:
        service = PostgresService(client=client)
        service.start()

    @abstractmethod
    def configure_postgres(self, platform: Platform) -> None:
        """Update framework_locals with the correct configuration for postgres"""
        pass

    # TODO teardown?
    # TODO generalize each service?
