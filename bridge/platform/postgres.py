from .base import Platform
from .render import build_render_postgres_environment
from bridge.service.postgres import PostgresEnvironment


def build_postgres_environment(platform: Platform) -> PostgresEnvironment:
    if platform == Platform.LOCAL:
        # This uses hardcoded default values,
        # and must match the values used in the PostgresService class
        # which runs locally.
        return PostgresEnvironment()
    elif platform == Platform.RENDER:
        return build_render_postgres_environment()
    elif platform == Platform.UNKNOWN_REMOTE:
        # This will pull from environment variables like POSTGRES_USER, etc.
        return PostgresEnvironment.from_env()
    else:
        raise ValueError(f"Unsupported platform for configuring Postgres: {platform}")
