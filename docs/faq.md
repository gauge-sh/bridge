# FAQ

### How does it work?

When running locally, Bridge uses Docker to create and manage containers for services like Postgres, Redis, and Celery. Since Bridge is included in your settings module, it automatically configures your Django application to connect to these services.

When you are ready to deploy, Bridge creates configuration files for Render that specify how to build and run your Django application alongside the same services. You can then connect your Render project to your GitHub repository and [deploy the Blueprint](https://docs.render.com/infrastructure-as-code#setup) (steps 3-8).

