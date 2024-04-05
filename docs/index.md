# bridge

---
Automate your local and deployed infra in one line.

#todo add gif

 

[docs]

### What is bridge?
Bridge enables you to seamlessly run and deploy all of the infrastructure you need for your python web application.

- Out of the box support for Django, FastAPI, and Flask
- One line of copy-paste configuration
- Local postgres database automatically configured and connected
- Local Redis and Celery instances automatically configured and connected
- Easy one-command deploy configuration for Render and Heroku

### Installation
```bash
pip install python-bridge
```
### Usage
Adding bridge to your project is incredibly simple.
```python
from bridge.framework.[framework] import configure

configure(locals())
```
<details>
<summary>Django</summary>
Place this code snippet at the end of your `settings.py` file:
<pre><code class="language-python">from bridge.framework.django import configure
configure(locals())
</code></pre>
</details>
<details>
<summary>Flask</summary>
Place this code snippet at the end of your `settings.py` file:
<pre><code class="language-python">from bridge.flask import configure
configure(locals())
</code></pre>
</details>
<details>
<summary>Fast API</summary>
Place this code snippet at the end of your `settings.py` file:
<pre><code class="language-python">from bridge.fastapi import configure
configure(locals())
</code></pre>
</details>


The next time you start up your application, bridge will create and configure local infrastructure for you.

### Deploys
Bridge can also handle deployed configuration for your app as well! Simply run
```bash
bridge init [heroku|render]
```
and bridge will create all of the configuration necessary for you to 1 click deploy onto either Heroku or Render's hosting solutions.


### Advanced usage
- turn on/off different services
- specify environment variables?


### TODO
- add support for celery, redis, mailhog/mail, jupyter
- add support for flask, fastapi, ...
- add support for `pip install python-bridge[redis,flask,etc]`

