import os
import sys
import tempfile
import uuid
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path
from time import sleep

import requests
from google.cloud import storage
from rich.console import Console

from bridge.console import log_error, log_task

API_URL = "https://api.bridge-cli.com/api/v0.1/deploy"


class DeployHandler(ABC):
    def __init__(self, bucket_name, project_root=".", deploy_name=None):
        self.python_path = (
            sys.executable
        )  # TODO need to better interpret and utilize this
        self.project_root = Path(os.path.abspath(project_root))
        self.bucket_name = bucket_name
        if not deploy_name:
            deploy_name = str(uuid.uuid4())
        self.deploy_name = deploy_name

    @abstractmethod
    def validate(self):
        """
        Perform framework-specific validation steps.
        Must be implemented by subclasses.
        """
        pass

    def bundle(self, temp_dir: tempfile.TemporaryDirectory) -> Path:
        with log_task(start_message="Bundling...", end_message="Project bundled"):
            zip_filename = f"{self.deploy_name}.zip"
            zip_path = Path(temp_dir) / zip_filename

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for file_path in self.project_root.rglob(
                    "*"
                ):  # TODO add .gitignore support
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(self.project_root))
        return zip_path

    def upload(self, zip_path: Path) -> str:
        with log_task(
            start_message="Uploading bundle...", end_message="Bundle uploaded"
        ):
            storage_client = storage.Client()
            bucket = storage_client.bucket(self.bucket_name)
            destination_blob_name = f"deploys/{self.deploy_name}.zip"
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(str(zip_path))
            public_url = blob.public_url
            return public_url

    def trigger(self, project_name, source_url):
        with log_task(
            start_message="Triggering deploy...", end_message="Deploy triggered"
        ):
            data = {
                "name": self.deploy_name[:8],
                "project_name": project_name,
                "source_url": source_url,
            }
            resp = requests.post(API_URL, json=data)
            if resp.status_code != 200:
                print(resp.status_code, resp.content)
                log_error("Failed to trigger the deploy")
                sys.exit(1)

    def retrieve(self):
        with log_task(
            start_message="Checking deploy status...", end_message="Status updated"
        ):
            status = "pending"
            while status == "pending":
                resp = requests.get(API_URL)
                sleep(0.1)
                if resp.status_code == 200:
                    deployment_data = resp.json()
                    for deployment in deployment_data["deployments"]:
                        if deployment["name"] == self.deploy_name[:8]:
                            status = deployment["status"]
                            if status == "error":
                                log_error(deployment["debug"])
                            elif status == "deployed":
                                return deployment.get("deploy_url", "[deployment_url]")
                            break
                else:
                    sleep(3)

    def deploy(self):
        console = Console()
        console.print(
            f"Deploying [bold white]{self.project_root.name}"
            f"[bold green] as [bold white]{self.deploy_name[:8]}[bold green]...",
        )
        self.validate()
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = self.bundle(temp_dir)
            url = self.upload(zip_path)
            project_name = (
                self.project_root.name
            )  # TODO we should infer an asgi or wsgi entrypoint
            self.trigger(project_name=project_name, source_url=url)
            deployment_url = self.retrieve()
        console.print(f"[bold white]{self.deploy_name[:8]} [bold green]deployed!")
        console.print(f"[blue]{deployment_url}")
