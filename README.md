[![image](https://img.shields.io/pypi/v/python-bridge.svg)](https://pypi.python.org/pypi/python-bridge)
[![image](https://img.shields.io/pypi/l/python-bridge.svg)](https://pypi.python.org/pypi/python-bridge)
[![image](https://img.shields.io/pypi/pyversions/python-bridge.svg)](https://pypi.python.org/pypi/python-bridge)
[![image](https://github.com/Never-Over/bridge/actions/workflows/ci.yml/badge.svg)](https://github.com/Never-Over/bridge/actions/workflows/ci.yml)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
# bridge
Fully automate your infrastructure for Django.

![](https://raw.githubusercontent.com/Never-Over/bridge/main/docs/runserver_demo.gif)

[Full Documentation](https://never-over.github.io/bridge/)

### What is bridge?
Bridge enables you to seamlessly run and deploy all the infrastructure you need for a complete Django project.

- Two lines of copy-paste configuration
- Local Postgres database automatically configured and connected
- Local Redis instance automatically configured and connected
- Local Celery and Celery Flower instance automatically configured and connected
- Easy one-command deploy configuration to Render

### Installation
Install [Docker](https://docs.docker.com/get-docker/) and verify it's running:
```bash
> docker version
Client: ...
```
Install bridge:
```bash
pip install python-bridge
```
### Usage
Add the following code to the end of your `settings.py` file (or `DJANGO_SETTINGS_MODULE`):
```python
from bridge.django import configure

configure(locals())
```


The next time you start up your application, bridge will create and configure local infrastructure for you:
```bash
> ./manage.py runserver

Setting up service bridge_postgres...
[12:00:00] ✓ Image postgres:12 pulled
[12:00:00] ✓ Container bridge_postgres started
[12:00:00] ✓ bridge_postgres is ready
Service bridge_postgres started!
Setting up service bridge_redis...
[12:00:00] ✓ Image redis:7.2.4 pulled
[12:00:00] ✓ Container bridge_redis started
[12:00:00] ✓ bridge_redis is ready
Service bridge_redis started!
Setting up service bridge_celery...
[12:00:00] ✓ Local worker started
Service bridge_celery started!
Setting up service bridge_flower...
[12:00:00] ✓ Flower started
Service bridge_flower started!
Performing system checks...

System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```
That's it! You now have all the local infrastructure you need to run your django application.

### Deploys
Bridge can also handle deployed configuration for your app as well! Simply run:
```bash
bridge init render
```
You may be prompted for the entrypoint of your application and settings file if bridge cannot detect them. 
Bridge will create all the configuration necessary for you to immediately deploy to [Render](https://render.com/). This includes a Blueprint `render.yaml` as well as build scripts and start scripts for your Django application.
After running `bridge init render`, commit the changes and visit your project on github. You will see the following button at the end of your README in the root of your repository:

![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)

To deploy your application to the world, simply click the button! Bridge will configure everything needed for Render to deploy and host your app.

In the future, we'll look into supporting more deployment runtimes such as Heroku, AWS, GCP, Azure, and more.

### FAQ

How does bridge work?
- Bridge spins up and runs all the services needed for your infrastructure in the background. Postgres and Redis run in docker containers, while Celery and Celery Flower (which need to understand your application code) run as background processes.

What if I don't need all the services that bridge provides?
- Bridge is designed to be modular. You can configure only the services you need by editing the `bridge.yaml` file that bridge creates in your project root. By default, `enable_postgres: true` and `enable_worker: true` are set, but you can change these to `false` to prevent bridge from configuring Postgres and Celery respectively.

How can I stop the services that bridge spins up?
- `bridge stop` will stop all running services.

How can I access the database directly?
- Locally, bridge provides access to a psql shell through `bridge db shell`. Remotely, [Render has instructions for connecting](https://docs.render.com/databases#connecting-with-the-external-url). 

How can I access redis directly?
- Bridge provides access to redis-cli through `bridge redis shell`. Remotely, [Render has instructions for connecting](https://docs.render.com/redis#connecting-using-redis-cli).

How can I access Celery?
- Flower is a web interface into all the information you need to debug and work with Celery. By default, bridge will run Flower on http://localhost:5555.
