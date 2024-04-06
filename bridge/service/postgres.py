import os
from time import sleep
from typing import Optional

import docker
import psycopg
from pydantic import BaseModel, Field

from bridge.console import log_task
from bridge.service.docker import ContainerConfig, DockerService
from bridge.utils.filesystem import resolve_dot_bridge


class PostgresEnvironment(BaseModel):
    user: str = "postgres"
    password: str = "postgres"
    db: str = "postgres"
    host: str = "localhost"
    port: str = "5432"

    @classmethod
    def from_env(cls):
        return cls(
            POSTGRES_USER=os.environ.get("POSTGRES_USER", "postgres"),
            POSTGRES_PASSWORD=os.environ.get("POSTGRES_PASSWORD", "postgres"),
            POSTGRES_DB=os.environ.get("POSTGRES_DB", "postgres"),
            POSTGRES_HOST=os.environ.get("POSTGRES_HOST", "localhost"),
            POSTGRES_PORT=os.environ.get("POSTGRES_PORT", "5432"),
        )


class PostgresConfig(ContainerConfig):
    image: str = "postgres:12"
    name: str = "bridge_postgres"
    ports: dict = {"5432/tcp": 5432}
    volumes: dict = Field(
        default_factory=lambda: {
            f"{resolve_dot_bridge()}/pgdata": {
                "bind": "/var/lib/postgresql/data",
                "mode": "rw",
            }
        }
    )
    environment: PostgresEnvironment = PostgresEnvironment()


class PostgresService(DockerService):
    def __init__(
        self, client: docker.DockerClient, config: Optional[PostgresConfig] = None
    ) -> None:
        super().__init__(client, config or PostgresConfig())

    def ensure_ready(self):
        dsn = (
            f"dbname={self.config.environment.db} "
            f"user={self.config.environment.user} "
            f"password={self.config.environment.password} "
            f"host={self.config.environment.host} "
            f"port={self.config.environment.port}"
        )
        with log_task(
            start_message=f"Waiting for [white]{self.config.name}[/white] to be ready",
            end_message=f"[white]{self.config.name}[/white] is ready",
        ):
            while True:
                try:
                    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
                        cur.execute("SELECT 1")
                        return
                except psycopg.OperationalError:
                    sleep(0.1)
