# FAQ

### How does it work locally?

When running locally, Bridge uses Docker to create and manage containers for Postgres and Redis. Since Bridge is included in your settings module, it automatically configures your Django application to connect to these services. Celery and Flower require your application code, and are spun up as background processes.

### How does it work with deployments?

When you are ready to deploy, Bridge creates configuration files for Render that specify how to build and run your Django application alongside the same services. Bridge also writes a "Deploy to Render" button straight into your README for added convenience! You can deploy your application by clicking the 'Deploy to Render' button shown on your project's GitHub page.

### What if I don't need all the services that bridge provides?

Bridge is designed to be modular. You can configure only the services you need by creating or editing the `bridge.yaml` file that Bridge creates in your project root. By default, `enable_postgres: true` and `enable_worker: true` are set, but you can change these to `false` to prevent bridge from configuring Postgres and Celery respectively.


### How can I stop the services that bridge spins up?
`bridge stop` will stop all running services.


### How can I access the database directly?
Locally, bridge provides access to a psql shell through `bridge db shell`. Remotely, [Render has instructions for connecting](https://docs.render.com/databases#connecting-with-the-external-url). 

### How can I access redis directly?
Bridge provides access to redis-cli through `bridge redis shell`. Remotely, [Render has instructions for connecting](https://docs.render.com/redis#connecting-using-redis-cli).

### How can I access Celery?
Flower is a web interface into all the information you need to debug and work with Celery. By default, bridge will run Flower on [http://localhost:5555](http://localhost:5555).
