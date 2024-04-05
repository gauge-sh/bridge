import os

import dj_database_url
from bridge.service.postgres import PostgresEnvironment


def build_render_postgres_environment() -> PostgresEnvironment:
    try:
        database_url = os.environ["DATABASE_URL"]
    except KeyError:
        raise ValueError("DATABASE_URL is required for Render Postgres")
    config = dj_database_url.config(
        default=database_url,
    )
    return PostgresEnvironment(
        host=config["HOST"],
        port=config["PORT"],
        db=config["NAME"],
        user=config["USER"],
        password=config["PASSWORD"],
    )
