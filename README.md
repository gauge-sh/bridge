# bridge

---
Automate your local and deployed infra in one line.

#todo add gif

 

[docs]

### What is bridge?
Bridge enables you to seamlessly run and deploy all the infrastructure you need for a complete Django project.

- One line of copy-paste configuration
- Local Postgres database automatically configured and connected
- Local Redis and Celery instances automatically configured and connected
- Easy one-command deploy configuration to Render

### Installation
```bash
pip install python-bridge
```
### Usage
Adding bridge to your project is incredibly simple:
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
and bridge will create all the configuration necessary for you to immediately deploy to [Render](https://render.com/).

In the future, we'll look into supporting more deployment runtimes such as Heroku, AWS, GCP, Azure, etc.

### FAQ

Local: celery logs, psql, flower?
Deployed: environment variables, etc.

### Advanced usage
- turn on/off different services
- specify environment variables?


### TODO
- add support for celery, redis, mailhog/mail, jupyter
- add support for flask, fastapi, ...
- add support for `pip install python-bridge[redis,flask,etc]`

