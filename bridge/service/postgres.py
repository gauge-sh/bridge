# Responsible for postgres
import os
from time import sleep


from bridge.service.docker import DockerService, ContainerConfig
import psycopg
from pydantic import BaseModel, Field
import docker


class PostgresEnvironment(BaseModel):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"


def resolve_pg_data_path():
    return os.path.abspath("./pgdata")


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
        print("Waiting for PostgreSQL to be ready...")
        dsn = (
            f"dbname={self.config.environment.POSTGRES_DB} "
            f"user={self.config.environment.POSTGRES_USER} "
            f"password={self.config.environment.POSTGRES_PASSWORD} "
            f"host={self.config.environment.POSTGRES_HOST} "
            f"port={self.config.environment.POSTGRES_PORT}"
        )
        while True:
            try:
                with psycopg.connect(dsn) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                        print("PostgreSQL is ready.")
                        return
            except psycopg.OperationalError:
                sleep(0.1)
