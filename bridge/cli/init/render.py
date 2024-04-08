import os
from pathlib import Path

from pydantic import BaseModel

from .templates import build_sh_template, render_yaml_template, start_sh_template
from bridge.utils.filesystem import (
    resolve_dot_bridge,
    resolve_project_dir,
    set_executable,
)
from bridge.console import console


def detect_application_callable(project_name: str = "") -> str:
    wsgi_path = f"{project_name}/wsgi.py"
    asgi_path = f"{project_name}/asgi.py"
    if os.path.exists(wsgi_path):
        return f"{project_name}.wsgi:application"
    elif os.path.exists(asgi_path):
        return f"{project_name}.asgi:application"
    else:
        return console.input(
            "Please provide the path to your WSGI or ASGI application callable (ex: myapp.wsgi:application):\n> "
        )


class RenderPlatformInitConfig(BaseModel):
    project_name: str
    app_path: str
    bridge_path: str


def build_render_init_config() -> RenderPlatformInitConfig:
    # NOTE: this method may request user input directly on the CLI
    #   to determine configuration when it cannot be auto-detected
    project_name = resolve_project_dir().name
    app_path = detect_application_callable(project_name=project_name)
    # May be able to remove this call since all scripts, YAML have moved to root
    bridge_path = resolve_dot_bridge()
    return RenderPlatformInitConfig(
        project_name=project_name, app_path=app_path, bridge_path=str(bridge_path)
    )


def initialize_render_platform(config: RenderPlatformInitConfig):
    build_sh_path = Path("./render-build.sh")
    with build_sh_path.open(mode="w") as f:
        f.write(build_sh_template())
    set_executable(build_sh_path)

    start_sh_path = Path("./render-start.sh")
    with start_sh_path.open(mode="w") as f:
        f.write(start_sh_template(app_path=config.app_path))
    set_executable(start_sh_path)

    with open("render.yaml", "w") as f:
        f.write(
            render_yaml_template(
                service_name=config.project_name,
                database_name=f"{config.project_name}-db",
            )
        )
