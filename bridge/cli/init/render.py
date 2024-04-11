import os
from abc import ABC, abstractmethod
from importlib.util import find_spec
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from rich.prompt import Confirm

from bridge.cli.errors import ActionCancelledError
from bridge.cli.init.templates import (
    build_sh_template,
    build_worker_sh_template,
    deploy_to_render_button_template,
    render_yaml_template,
    start_sh_template,
    start_worker_sh_template,
)
from bridge.cli.init.templates.deploy_to_render_button import button_exists_in_content
from bridge.console import console, log_warning
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
    settings_path = Path(project_name) / "settings.py"
    if os.path.exists(settings_path):
        return f"{project_name}.settings"
    else:
        while True:
            module_path = console.input(
                "Please provide the path to your"
                " Django settings module (ex: myapp.settings):\n> "
            )
            if find_spec(module_path) is not None:
                # The module exists and can be imported
                return module_path
            else:
                console.print(
                    f"The module {module_path} could not be found. Please try again."
                )


def detect_application_callable(project_name: str = "") -> str:
    project_path = Path(project_name)
    wsgi_path = project_path / "wsgi.py"
    asgi_path = project_path / "asgi.py"
    if os.path.exists(wsgi_path):
        return f"{project_name}.wsgi:application"
    elif os.path.exists(asgi_path):
        return f"{project_name}.asgi:application"

    # If we haven't returned yet, it means we could not auto-detect the callable
    while True:
        user_input = console.input(
            "Please provide the path to your WSGI or ASGI application callable "
            "(ex: myapp.wsgi:application):\n> "
        )
        module_path, _, callable_name = user_input.partition(":")
        if not callable_name:
            callable_name = "application"  # Default to 'application' if not provided
        try:
            if find_spec(module_path) is not None:
                return f"{module_path}:{callable_name}"
            else:
                console.print(
                    f"The module '{module_path}' could not be found or imported."
                    " Please try again."
                )
        except ImportError:
            console.print(
                f"The module '{module_path}' could not be found or imported."
                " Please try again."
            )


class DjangoConfig(BaseModel):
    settings_module: str


class RenderPlatformInitConfig(BaseModel):
    framework: Framework = Framework.DJANGO
    project_name: str
    app_path: str
    bridge_path: str
    django_config: Optional[DjangoConfig] = None

    @property
    def script_dir(self) -> str:
        return f"bridge-{self.framework.value}-render"


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

    os.makedirs(init_config.script_dir, exist_ok=True)
    if any(os.path.exists(file.PATH) for file in TEMPLATED_FILES):
        log_warning("Configuration files already exist.")
        if not Confirm.ask("Do you want to overwrite them? [y/N]", console=console):
            raise ActionCancelledError("Not overwriting existing configuration files.")

    return init_config


class TemplatedFile(ABC):
    PATH: Path
    EXECUTABLE: bool = False

    @classmethod
    @abstractmethod
    def build(cls, config: RenderPlatformInitConfig) -> str: ...

    @classmethod
    def write(cls, config: RenderPlatformInitConfig):
        # For now, assume executables always belong in the script_dir
        prefix_path = Path(config.script_dir) if cls.EXECUTABLE else None
        path = prefix_path / cls.PATH if prefix_path else cls.PATH
        with path.open(mode="w") as f:
            f.write(cls.build(config=config))
        if cls.EXECUTABLE:
            set_executable(path)


class BuildSh(TemplatedFile):
    PATH = Path("build.sh")
    EXECUTABLE = True

    @classmethod
    def build(cls, config: RenderPlatformInitConfig) -> str:
        return build_sh_template(framework=config.framework)


class BuildWorkerSh(TemplatedFile):
    PATH = Path("build-worker.sh")
    EXECUTABLE = True

    @classmethod
    def build(cls, config: RenderPlatformInitConfig) -> str:
        return build_worker_sh_template(framework=config.framework)


class StartSh(TemplatedFile):
    PATH = Path("start.sh")
    EXECUTABLE = True

    @classmethod
    def build(cls, config: RenderPlatformInitConfig) -> str:
        return start_sh_template(app_path=config.app_path)


class StartWorkerSh(TemplatedFile):
    PATH = Path("start-worker.sh")
    EXECUTABLE = True

    @classmethod
    def build(cls, config: RenderPlatformInitConfig) -> str:
        return start_worker_sh_template(framework=config.framework)


class RenderYaml(TemplatedFile):
    PATH = Path("render.yaml")

    @classmethod
    def build(cls, config: RenderPlatformInitConfig) -> str:
        return render_yaml_template(
            framework=config.framework,
            script_dir=config.script_dir,
            service_name=config.project_name,
            database_name=f"{config.project_name}_db",
            django_settings_module=config.django_config.settings_module
            if config.django_config
            else "",
        )


TEMPLATED_FILES = [
    BuildSh,
    BuildWorkerSh,
    StartSh,
    StartWorkerSh,
    RenderYaml,
]


def add_deploy_render_button_to_readme():
    # NOTE: assumes we are in the project dir
    if os.path.exists("README.md"):
        with open("README.md") as f:
            if button_exists_in_content(f.read()):
                # Button already in README, don't write anything to the file
                return
        with open("README.md", "a") as f:
            f.write(deploy_to_render_button_template())
    else:
        with open("README.md", "w") as f:
            f.write(deploy_to_render_button_template())


def initialize_render_platform(config: RenderPlatformInitConfig):
    add_deploy_render_button_to_readme()
    for file in TEMPLATED_FILES:
        file.write(config)
