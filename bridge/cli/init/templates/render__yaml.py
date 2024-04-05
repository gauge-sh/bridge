template = """#################################################################
# Example render.yaml                                           #
# Do not use this file directly! Consult it for reference only. #
#################################################################

services:
  # A web service on the Ruby native runtime
  - type: web
    runtime: ruby
    name: sinatra-app
    repo: https://github.com/render-examples/sinatra # Default: Repo containing render.yaml
    numInstances: 3   # Manual scaling configuration. Default: 1
    region: frankfurt # Default: oregon
    plan: standard    # Default: starter
    branch: prod      # Default: master
    buildCommand: bundle install
    preDeployCommand: bundle exec ruby migrate.rb
    startCommand: bundle exec ruby main.rb
    autoDeploy: false # Disable automatic deploys
    maxShutdownDelaySeconds: 120 # Increase graceful shutdown period. Default: 30, Max: 300
    domains: # Custom domains
      - example.com
      - www.example.org
    envVars: # Environment variables
      - key: API_BASE_URL
        value: https://api.example.com # Hardcoded value
      - key: APP_SECRET
        generateValue: true # Generate a base64-encoded 256-bit value
      - key: STRIPE_API_KEY
        sync: false # Prompt for a value in the Render Dashboard
      - key: DATABASE_URL
        fromDatabase: # Reference a property of a database (see available properties below)
          name: mydatabase
          property: connectionString
      - key: MINIO_PASSWORD
        fromService: # Reference a value from another service
          name: minio
          type: pserv
          envVarKey: MINIO_ROOT_PASSWORD
      - fromGroup: my-env-group # Add all variables from an environment group

  # A web service that builds from a Dockerfile
  - type: web
    runtime: docker
    name: webdis
    repo: https://github.com/render-examples/webdis.git # Default: Repo containing render.yaml
    rootDir: webdis # Default: Repo root
    dockerCommand: ./webdis.sh # Default: Dockerfile CMD
    scaling: # Autoscaling configuration
      minInstances: 1
      maxInstances: 3
      targetMemoryPercent: 60 # Optional if targetCPUPercent is set
      targetCPUPercent: 60    # Optional if targetMemory is set
    healthCheckPath: /
    registryCredential: # Default: No credential
      fromRegistryCreds:
        name: my-credentials
    envVars:
      - key: REDIS_HOST
        fromService: # Reference a property from another service (see available properties below)
          type: redis
          name: lightning
          property: host
      - key: REDIS_PORT
        fromService:
          type: redis
          name: lightning
          property: port
      - fromGroup: conc-settings

  # A private service with an attached persistent disk
  - type: pserv
    runtime: docker
    name: minio
    repo: https://github.com/render-examples/minio.git # Default: Repo containing render.yaml
    envVars:
    - key: MINIO_ROOT_PASSWORD
      generateValue: true # Generate a base64-encoded 256-bit value
    - key: MINIO_ROOT_USER
      sync: false # Prompt for a value in the Render Dashboard
    - key: PORT
      value: 10000
    disk: # Persistent disk configuration
      name: data
      mountPath: /data
      sizeGB: 10 # optional

# A Python cron job that runs every hour
  - type: cron
    name: date
    runtime: python
    schedule: "0 * * * *"
    buildCommand: "true" # ensure it's a string
    startCommand: date
    repo: https://github.com/render-examples/docker.git # optional

# A Dockerfile-based background worker
  - type: worker
    name: queue
    runtime: docker
    dockerfilePath: ./sub/Dockerfile # Optional
    dockerContext: ./sub/src # Optional
    branch: queue # Optional

# A static site
  - type: web
    name: my-blog
    runtime: static
    buildCommand: yarn build
    staticPublishPath: ./build
    pullRequestPreviewsEnabled: true # Enable service previews
    buildFilter:
      paths:
      - src/**/*.js
      ignoredPaths:
      - src/**/*.test.js
    headers:
      - path: /*
        name: X-Frame-Options
        value: sameorigin
    routes:
      - type: redirect
        source: /old
        destination: /new
      - type: rewrite
        source: /a/*
        destination: /a

# A Redis instance
  - type: redis
    name: lightning
    ipAllowList: # Required
      - source: 0.0.0.0/0
        description: everywhere
    plan: free # Default: starter
    maxmemoryPolicy: noeviction # Default: allkeys-lru

# List all PostgreSQL databases here
databases:

  # A database with a read replica
  - name: elephant
    databaseName: mydb # Optional (Render may add a suffix)
    user: adrian # Optional
    ipAllowList: # Optional (defaults to allow all)
      - source: 203.0.113.4/30
        description: office
      - source: 198.51.100.1
        description: home
    readReplicas:
      - name: elephant-replica

  # A database that allows only private network connections
  - name: private database
    databaseName: private
    ipAllowList: [] # No entries in the IP allow list

  # A database that enables high availability
  - name: highly available database
    plan: pro
    highAvailability:
      enabled: true

# Environment groups
envVarGroups:
  - name: conc-settings
    envVars:
      - key: CONCURRENCY
        value: 2
      - key: SECRET
        generateValue: true
  - name: stripe
    envVars:
      - key: STRIPE_API_URL
        value: https://api.stripe.com/v2
"""


def render_yaml_template() -> str:
    return template.format()
