import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

import docker

from bridge.config import BridgeConfig
from bridge.platform import Platform, detect_platform
from bridge.service.postgres import PostgresService
from bridge.service.redis import RedisService


class Framework(Enum):
    DJANGO = "django"
    FLASK = "flask"
    FASTAPI = "fastapi"


class FrameWorkHandler(ABC):
    FRAMEWORK: Framework = NotImplemented

    def __init__(
        self,
        project_name: str,
        framework_locals: dict[Any, Any],
        bridge_config: BridgeConfig,
    ):
        self.project_name = project_name
        self.framework_locals = framework_locals
        self.enable_postgres = bridge_config.enable_postgres
        self.enable_worker = bridge_config.enable_worker

    def is_remote(self) -> bool:
        """
        Check if the application seems to be running on a remote platform.
        Specific frameworks may be able to detect this more accurately and
        should override this method.
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
            # NOTE: worker and flower MUST be configured last, since they
            # will read the framework locals immediately
            self.configure_worker(platform=platform)

    def start_local_services(self):
        """Start local services if necessary"""
        client = docker.from_env()
        if self.enable_postgres:
            self.start_local_postgres(client)
        if self.enable_worker:
            self.start_local_redis(client)
            self.start_local_worker()
            self.start_local_flower()

    def start_local_postgres(self, client: docker.DockerClient) -> None:
        service = PostgresService(client=client)
        service.start()

    def start_local_redis(self, client: docker.DockerClient) -> None:
        service = RedisService(client=client)
        service.start()

    @abstractmethod
    def start_local_worker(self) -> None:
        """start a local celery instance configured for the correct framework"""
        pass

    @abstractmethod
    def start_local_flower(self) -> None:
        """start a local celery flower instance configured for the correct framework"""

    @abstractmethod
    def configure_postgres(self, platform: Platform) -> None:
        """Update framework_locals with the correct configuration for postgres"""
        pass

    @abstractmethod
    def configure_worker(self, platform: Platform) -> None:
        """Update framework_locals with the correct configuration for celery"""
        pass
