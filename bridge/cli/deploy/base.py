import sys
import tempfile
import uuid
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path

from google.cloud import storage


class DeployHandler(ABC):
    def __init__(self, bucket_name, project_root=".", deploy_name=None):
        self.python_path = (
            sys.executable
        )  # TODO need to better interpret and utilize this
        self.project_root = Path(project_root)
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
        zip_filename = f"{self.deploy_name}.zip"
        zip_path = Path(temp_dir) / zip_filename

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.project_root.rglob(
                "*"
            ):  # TODO add .gitignore support
                if file_path.is_file():
                    zipf.write(file_path, file_path.relative_to(self.project_root))
        print(f"Directory '{self.project_root}' has been zipped into {zip_path}")
        return zip_path

    def upload(self, zip_path: Path):
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        destination_blob_name = f"deploys/{uuid.uuid4()}.zip"
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(str(zip_path))
        print(f"File {zip_path} uploaded to {destination_blob_name}.")

    def deploy(self):
        print("Running pre-deploy checks...")
        self.validate()
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = self.bundle(temp_dir)
            self.upload(zip_path)
