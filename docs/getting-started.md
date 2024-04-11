# Getting Started

Bridge includes an SDK and CLI tool which operate within your Django project. This page will guide you through the process of installing and configuring Bridge.

## Requirements
Bridge requires **[Docker](https://docs.docker.com/get-docker/)** to be installed on your machine.

## Installation
```bash
pip install python-bridge
```

## Usage
Adding bridge to your project is incredibly simple.

Add the following code to the end of your `settings.py` file (or `DJANGO_SETTINGS_MODULE`):
```python
# Configure infrastructure with Bridge. All other settings should be above this line.
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
Performing system checks...

System check identified no issues (0 silenced).
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```
That's it! You now have all the local infrastructure you need to run your Django application.

## Deployment
Bridge handles your deployed infrastructure settings without changing any code! Simply run:
```bash
bridge init render
```
and bridge will create all the configuration necessary for you to immediately deploy to [Render](https://render.com/).

This includes a Blueprint `render.yaml` as well as build scripts and start scripts for your Django application.

To deploy your application, follow the steps outlined in the [Render documentation](https://docs.render.com/infrastructure-as-code#setup) (steps 3-8).
