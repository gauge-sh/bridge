import os
from abc import ABC, abstractmethod

import docker

from bridge.platform import Platform, detect_platform
from bridge.service.postgres import PostgresService
from bridge.service.redis import RedisConfig, RedisService


class FrameWorkHandler(ABC):
    def __init__(
        self,
        project_name: str,
        framework_locals: dict,
        enable_postgres: bool,
        enable_worker: bool,
    ):
        self.project_name = project_name
        self.framework_locals = framework_locals
        self.enable_postgres = enable_postgres
        self.enable_worker = enable_worker

    def is_remote(self) -> bool:
        """
        Check if the application seems to be running on a remote platform.
        Specific frameworks may be able to detect this more accurately and should override this method.
        """
        return bool(os.environ.get("BRIDGE_PLATFORM"))

    def run(self) -> None:
        """Start services."""
        platform = detect_platform() if self.is_remote() else Platform.LOCAL
        self.configure_services(platform)
        if platform == Platform.LOCAL:
            self.start_local_services()

    def configure_services(self, platform: Platform) -> None:
        if self.enable_postgres:
            self.configure_postgres(platform=platform)
        if self.enable_worker:
            self.configure_worker(platform=platform)

    def start_local_services(self):
        """Start local services if necessary"""
        client = docker.from_env()
        if self.enable_postgres:
            self.start_local_postgres(client)
        if self.enable_worker:
            self.start_local_redis(client)
            self.start_local_worker()

    def start_local_postgres(self, client: docker.DockerClient) -> None:
        service = PostgresService(client=client)
        service.start()

    def start_local_redis(self, client: docker.DockerClient) -> None:
        config = RedisConfig()
        service = RedisService(client=client, config=config)
        service.start()

    @abstractmethod
    def start_local_worker(self) -> None:
        """start a local celery instance configured for the correct framework"""
        pass

    @abstractmethod
    def configure_postgres(self, platform: Platform) -> None:
        """Update framework_locals with the correct configuration for postgres"""
        pass

    @abstractmethod
    def configure_worker(self, platform: Platform) -> None:
        """Update framework_locals with the correct configuration for postgres"""
        pass
