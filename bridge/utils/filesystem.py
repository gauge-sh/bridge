import os
import stat
import sys
from pathlib import Path

from bridge.console import log_error


def set_executable(file_path: Path) -> None:
    file_path.chmod(
        file_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )


def resolve_project_dir() -> Path:
    current_dir = os.getcwd()
    manage_py_path = Path(os.path.join(current_dir, "manage.py"))
    if not manage_py_path.exists():
        log_error(
            f"No manage.py file found in {os.getcwd()}. "
            f"Run the command from the same directory as manage.py"
        )
        sys.exit(1)

    return Path(current_dir)


def resolve_dot_bridge() -> Path:
    project_dir = resolve_project_dir()

    def _create(path: str, is_file: bool = False, file_content: str = "") -> None:
        if not os.path.exists(path):
            if is_file:
                with open(path, "w") as f:
                    f.write(file_content.strip())
            else:
                os.makedirs(path)

    # Create .bridge
    bridge_path = os.path.join(project_dir, ".bridge")
    _create(bridge_path)
    # Create pgdata
    pgdata_path = os.path.join(bridge_path, "pgdata")
    _create(pgdata_path)
    # Create .gitignore
    gitignore_content = """
# This folder is for bridge configuration. Do not edit.

# gitignore all content, including this .gitignore
*
    """
    gitignore_path = os.path.join(bridge_path, ".gitignore")
    _create(gitignore_path, is_file=True, file_content=gitignore_content)
    return Path(bridge_path)
