from bridge.framework.base import Framework
from bridge.utils.sanitize import sanitize_postgresql_identifier

postgres_template = """
databases:
  - name: {service_name}-db
    plan: free
    databaseName: {database_name}
    user: {database_user}
"""

postgres_app_env_template = """      - key: DATABASE_URL
        fromDatabase:
          name: {service_name}-db
          property: connectionString"""


worker_template = """
  - type: redis
    name: {service_name}-redis
    plan: free
    ipAllowList: []
  - type: worker
    name: {service_name}-worker
    runtime: python
    buildCommand: ./{script_dir}/build-worker.sh
    startCommand: ./{script_dir}/start-worker.sh
    envVars:
      - key: BRIDGE_PLATFORM
        value: render
      - key: DJANGO_SETTINGS_MODULE
        value: {django_settings_module}
      - key: SECRET_KEY
        generateValue: true
      - key: TASK_CONCURRENCY
        value: 4
      - key: DEBUG
        value: "False"
      - key: DATABASE_URL
        fromDatabase:
          name: {service_name}-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: {service_name}-redis
          type: redis
          property: connectionString
"""

worker_app_env_template = """      - key: REDIS_URL
        fromService:
          name: {service_name}-redis
          type: redis
          property: connectionString"""


template = """services:
  - type: web
    plan: starter
    runtime: python
    name: {service_name}
    buildCommand: ./{script_dir}/build.sh
    startCommand: ./{script_dir}/start.sh
    envVars:
      - key: BRIDGE_PLATFORM
        value: render
      - key: SECRET_KEY
        generateValue: true
      - key: WEB_CONCURRENCY
        value: 4
      - key: DEBUG
        value: "False"
{postgres_app_env}
{worker_app_env}
{worker_service}
{postgres_service}
"""


def render_yaml_template(
    framework: Framework,
    script_dir: str,
    service_name: str,
    enable_postgres: bool = True,
    enable_worker: bool = True,
    database_name: str = "",
    database_user: str = "",
    django_settings_module: str = "",
) -> str:
    # TODO: use a real templating engine
    if framework != Framework.DJANGO:
        raise NotImplementedError(
            f"Unsupported framework for Render platform: {framework}"
        )

    if not django_settings_module:
        raise ValueError(
            "Failed to template render.yaml:"
            " DJANGO_SETTINGS_MODULE is required for Django projects"
        )

    if enable_postgres:
        database_name = database_name or service_name
        database_user = database_user or service_name
        postgres_service = postgres_template.format(
            service_name=service_name,
            database_name=sanitize_postgresql_identifier(database_name),
            database_user=sanitize_postgresql_identifier(database_user),
        )
        postgres_app_env = postgres_app_env_template.format(service_name=service_name)
    else:
        postgres_service = ""
        postgres_app_env = ""

    if enable_worker:
        worker_service = worker_template.format(
            service_name=service_name,
            script_dir=script_dir,
            django_settings_module=django_settings_module,
        )
        worker_app_env = worker_app_env_template.format(service_name=service_name)
    else:
        worker_service = ""
        worker_app_env = ""

    return (
        template.format(
            script_dir=script_dir,
            service_name=service_name,
            postgres_app_env=postgres_app_env,
            worker_app_env=worker_app_env,
            worker_service=worker_service,
            postgres_service=postgres_service,
        ).rstrip()
        + "\n"
    )
