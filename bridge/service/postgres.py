import logging
import os
import sys
from time import sleep, time

import docker  # type: ignore[import-untyped]
import psycopg
from pydantic import BaseModel, Field

from bridge.console import log_error, log_task
from bridge.service.docker import ContainerConfig, DockerService
from bridge.utils.filesystem import resolve_dot_bridge

logger = logging.getLogger(__name__)


class PostgresEnvironment(BaseModel):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    @property
    def dsn(self) -> str:
        return (
            f"dbname={self.POSTGRES_DB} "
            f"user={self.POSTGRES_USER} "
            f"password={self.POSTGRES_PASSWORD} "
            f"host={self.POSTGRES_HOST} "
            f"port={self.POSTGRES_PORT}"
        )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


class PostgresConfig(ContainerConfig[PostgresEnvironment]):
    image: str = "postgres:12"
    name: str = "bridge_postgres"
    ports: dict[str, int] = {"5432/tcp": 5432}
    volumes: dict[str, list[str] | dict[str, str]] = Field(
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
        self, client: docker.DockerClient, config: PostgresConfig | None = None
    ) -> None:
        super().__init__(client, config or PostgresConfig())

    def ensure_ready(self):
        dsn = self.config.environment.dsn
        msg = f"DSN: {dsn}"
        print(msg)
        with log_task(
            start_message=f"Waiting for [white]{self.config.name}[/white] to be ready",
            end_message=f"[white]{self.config.name}[/white] is ready",
        ):
            timeout = 30  # Set the timeout value in seconds
            start_time = time()  # Get the current time

            while True:
                if time() - start_time > timeout:
                    log_error("Not getting a response from the database. Exiting...")
                    sys.exit(1)

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
