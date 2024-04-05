import os
import sys
from pathlib import Path

from bridge.console import log_error


def resolve_dot_bridge() -> str:  # TODO return path objects instead of strings
    current_dir = os.getcwd()
    manage_py_path = Path(os.path.join(current_dir, "manage.py"))
    if not manage_py_path.exists():
        log_error(
            f"No manage.py file found in {os.getcwd()}. Run the command from the same directory as manage.py"
        )
        sys.exit(1)

    def _create(path: str, is_file=False, file_content: str = "") -> None:
        if not os.path.exists(path):
            if is_file:
                with open(path, "w") as f:
                    f.write(file_content.strip())
            else:
                os.makedirs(path)

    # Create .bridge
    bridge_path = os.path.join(current_dir, ".bridge")
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
    return bridge_path
