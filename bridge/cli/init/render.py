import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from bridge.cli.init.templates import (
    build_sh_template,
    render_yaml_template,
    start_sh_template,
    start_worker_sh_template,
)
from bridge.console import console
from bridge.framework.base import Framework
from bridge.utils.filesystem import (
    resolve_dot_bridge,
    resolve_project_dir,
    set_executable,
)


def detect_framework() -> Framework:
    # TODO: auto-detect framework (assuming Django)
    return Framework.DJANGO


def detect_django_settings_module(project_name: str = "") -> str:
    settings_path = f"{project_name}/settings.py"
    if os.path.exists(settings_path):
        return f"{project_name}.settings"
    else:
        # TODO: validate input
        return console.input(
            "Please provide the path to your"
            " Django settings module (ex: myapp.settings):\n> "
        )


def detect_application_callable(project_name: str = "") -> str:
    wsgi_path = f"{project_name}/wsgi.py"
    asgi_path = f"{project_name}/asgi.py"
    if os.path.exists(wsgi_path):
        return f"{project_name}.wsgi:application"
    elif os.path.exists(asgi_path):
        return f"{project_name}.asgi:application"
    else:
        # TODO: validate input
        return console.input(
            "Please provide the path to your WSGI or ASGI application callable "
            "(ex: myapp.wsgi:application):\n> "
        )


class DjangoConfig(BaseModel):
    settings_module: str


class RenderPlatformInitConfig(BaseModel):
    framework: Framework = Framework.DJANGO
    project_name: str
    app_path: str
    bridge_path: str
    django_config: Optional[DjangoConfig] = None


def build_render_init_config() -> RenderPlatformInitConfig:
    # NOTE: this method may request user input directly on the CLI
    #   to determine configuration when it cannot be auto-detected
    framework = detect_framework()
    project_name = resolve_project_dir().name
    app_path = detect_application_callable(project_name=project_name)
    bridge_path = resolve_dot_bridge()
    init_config = RenderPlatformInitConfig(
        project_name=project_name, app_path=app_path, bridge_path=str(bridge_path)
    )

    # Provide framework-specific configuration
    if framework == Framework.DJANGO:
        settings_module = detect_django_settings_module(project_name=project_name)
        init_config.django_config = DjangoConfig(settings_module=settings_module)

    return init_config


def initialize_render_platform(config: RenderPlatformInitConfig):
    build_sh_path = Path("./render-build.sh")
    with build_sh_path.open(mode="w") as f:
        f.write(build_sh_template(framework=config.framework))
    set_executable(build_sh_path)

    start_sh_path = Path("./render-start.sh")
    with start_sh_path.open(mode="w") as f:
        f.write(start_sh_template(app_path=config.app_path))
    set_executable(start_sh_path)

    start_worker_sh_path = Path("./render-start-worker.sh")
    with start_worker_sh_path.open(mode="w") as f:
        f.write(start_worker_sh_template(framework=config.framework))
    set_executable(start_worker_sh_path)

    with open("render.yaml", "w") as f:
        f.write(
            render_yaml_template(
                framework=config.framework,
                service_name=config.project_name,
                database_name=f"{config.project_name}_db",
                django_settings_module=config.django_config.settings_module
                if config.django_config
                else "",
            )
        )
