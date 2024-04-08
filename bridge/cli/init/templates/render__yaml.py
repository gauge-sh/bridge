from bridge.utils.sanitize import sanitize_postgresql_identifier

template = """services:
  - type: web
    plan: starter
    runtime: python
    name: {service_name}
    buildCommand: ./render-build.sh
    startCommand: ./render-start.sh
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: {service_name}-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: {service_name}-redis
          type: redis
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: WEB_CONCURRENCY
        value: 4
      - key: BRIDGE_PLATFORM
        value: render
  - type: redis
    name: {service_name}-redis
    plan: free
    ipAllowList: []

databases:
  - name: {service_name}-db
    plan: free
    databaseName: {database_name}
    user: {database_user}
"""


def render_yaml_template(
    service_name: str, database_name: str = "", database_user: str = ""
) -> str:
    database_name = database_name or service_name
    database_user = database_user or service_name
    return template.format(
        service_name=service_name,
        database_name=sanitize_postgresql_identifier(database_name),
        database_user=sanitize_postgresql_identifier(database_user),
    )
