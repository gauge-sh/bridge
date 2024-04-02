import subprocess
import sys

from bridge.cli.deploy.base import DeployHandler
from bridge.console import log_error, log_task


class DjangoDeployer(DeployHandler):
    def __init__(self, bucket_name: str, project_root="."):
        super().__init__(bucket_name, project_root)

    def validate(self):
        with log_task(
            start_message="Validating Django project integrity...",
            end_message="Django project valid",
        ):
            manage_py_path = self.project_root / "manage.py"
            if not manage_py_path.exists():
                log_error(f"No manage.py file found in {self.project_root}")
                sys.exit(1)

            try:
                subprocess.run(
                    [self.python_path, str(manage_py_path), "check"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                log_error("Found 'manage.py', but 'python manage.py check' failed")
                print(e.stdout, e.stderr)
                raise
