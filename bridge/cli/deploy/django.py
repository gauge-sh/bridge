import subprocess

from bridge.cli.deploy.base import DeployHandler


class DjangoDeployer(DeployHandler):
    def __init__(self, bucket_name: str, project_root="."):
        super().__init__(bucket_name, project_root)

    def validate(self):
        manage_py_path = self.project_root / "manage.py"
        if not manage_py_path.exists():
            print("No 'manage.py' found in the current directory.")
            raise SystemExit(1)

        try:
            subprocess.run(
                [self.python_path, str(manage_py_path), "check"],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print("Found 'manage.py', but 'python manage.py check' failed:")
            print(e.stdout, e.stderr)
            raise
