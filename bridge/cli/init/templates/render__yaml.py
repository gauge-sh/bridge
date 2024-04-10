from bridge.framework.base import Framework
from bridge.utils.sanitize import sanitize_postgresql_identifier

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
      - key: DATABASE_URL
        fromDatabase:
          name: {service_name}-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: {service_name}-redis
          type: redis
          property: connectionString
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

databases:
  - name: {service_name}-db
    plan: free
    databaseName: {database_name}
    user: {database_user}
"""


def render_yaml_template(
    framework: Framework,
    script_dir: str,
    service_name: str,
    database_name: str = "",
    database_user: str = "",
    django_settings_module: str = "",
) -> str:
    if framework != Framework.DJANGO:
        # TODO: use a real templating engine to allow flexibility across frameworks
        raise NotImplementedError(
            f"Unsupported framework for Render platform: {framework}"
        )

    if not django_settings_module:
        raise ValueError(
            "Failed to template render.yaml:"
            " DJANGO_SETTINGS_MODULE is required for Django projects"
        )

    database_name = database_name or service_name
    database_user = database_user or service_name
    return template.format(
        script_dir=script_dir,
        service_name=service_name,
        database_name=sanitize_postgresql_identifier(database_name),
        database_user=sanitize_postgresql_identifier(database_user),
        django_settings_module=django_settings_module,
    )
