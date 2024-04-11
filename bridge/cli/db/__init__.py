import docker

from bridge.service.postgres import PostgresService


def open_database_shell():
    client = docker.from_env()
    postgres_service = PostgresService(client=client)
    postgres_service.start()
    postgres_service.shell()
