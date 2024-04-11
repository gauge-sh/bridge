import os
from time import sleep
from typing import Optional, Union

import docker
import psycopg
from pydantic import BaseModel, Field

from bridge.console import log_task
from bridge.service.docker import ContainerConfig, DockerService
from bridge.utils.filesystem import resolve_dot_bridge


class PostgresEnvironment(BaseModel):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"


class PostgresConfig(ContainerConfig[PostgresEnvironment]):
    image: str = "postgres:12"
    name: str = "bridge_postgres"
    ports: dict[str, int] = {"5432/tcp": 5432}
    volumes: dict[str, Union[list[str], dict[str, str]]] = Field(
        default_factory=lambda: {
            str(resolve_dot_bridge() / "pgdata"): {
                "bind": "/var/lib/postgresql/data",
                "mode": "rw",
            }
        }
    )
    environment: PostgresEnvironment = Field(default_factory=PostgresEnvironment)


class PostgresService(DockerService[PostgresConfig]):
    def __init__(
        self, client: docker.DockerClient, config: Optional[PostgresConfig] = None
    ) -> None:
        super().__init__(client, config or PostgresConfig())

    def ensure_ready(self):
        dsn = (
            f"dbname={self.config.environment.POSTGRES_DB} "
            f"user={self.config.environment.POSTGRES_USER} "
            f"password={self.config.environment.POSTGRES_PASSWORD} "
            f"host={self.config.environment.POSTGRES_HOST} "
            f"port={self.config.environment.POSTGRES_PORT}"
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

    def shell(self):
        # Open a shell to the Postgres container
        # NOTE: This entirely replaces the currently running process!
        os.execvp(
            "docker",
            [
                "docker",
                "exec",
                "-it",
                self.config.name,
                "psql",
                "-U",
                self.config.environment.POSTGRES_USER,
                "-d",
                self.config.environment.POSTGRES_DB,
                "-h",
                self.config.environment.POSTGRES_HOST,
                "-p",
                self.config.environment.POSTGRES_PORT,
            ],
        )
