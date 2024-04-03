# Responsible for postgres
import os
from time import sleep

import docker
import psycopg
from pydantic import BaseModel, Field

from bridge.console import log_task
from bridge.service.docker import ContainerConfig, DockerService


class PostgresEnvironment(BaseModel):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"


def resolve_pg_data_path():
    # TODO create a folder per project or separate db for each
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.join(current_file_dir, "pgdata")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


class PostgresConfig(ContainerConfig):
    image: str = "postgres:12"
    name: str = "bridge_postgres"
    ports: dict = {"5432/tcp": 5432}
    volumes: dict = Field(
        default_factory=lambda: {
            resolve_pg_data_path(): {"bind": "/var/lib/postgresql/data", "mode": "rw"}
        }
    )
    environment: PostgresEnvironment = PostgresEnvironment()


class PostgresService(DockerService):
    def __init__(self, client: docker.DockerClient, config: PostgresConfig) -> None:
        super().__init__(client, config)

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
