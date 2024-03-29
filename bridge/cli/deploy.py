import os
import subprocess
import tempfile
import uuid
import zipfile
from pathlib import Path

from google.cloud import storage


def validate():
    """
    Check if the current directory is a valid Django project by attempting
    to run 'manage.py check'.
    """
    result = subprocess.run(["which", "python"], capture_output=True, text=True)
    python_path = result.stdout[:-1]
    print("local python path:", python_path)
    manage_py_path = Path("manage.py")
    if not manage_py_path.exists():
        print("No 'manage.py' found in the current directory.")
        raise SystemExit(1)
    result = subprocess.run(
        [python_path, "manage.py", "check"], capture_output=True, text=True, check=True
    )

    if result.returncode == 0:
        print(result.stdout)
    else:
        print("Found 'manage.py', but 'python manage.py check' failed:")
        print(result.stdout)
        print(result.stderr)
        raise


def bundle(output_path, root_dir="."):
    """Zip the current directory into the specified output path."""
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, root_dir))
    print(f"Directory '{root_dir}' has been zipped into {output_path}")


def upload(bucket_name, source_file_path, destination_blob_name):
    """Uploads a file to the specified GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_path)
    print(f"File {source_file_path} uploaded.")


def deploy(args):
    print("Running pre-deploy checks...")
    validate()
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_filename = f"deploy-{uuid.uuid4()}.zip"
        temp_zip_path = os.path.join(temp_dir, zip_filename)

        # Zip the current directory
        bundle(temp_zip_path)

        # Set these to your specific GCS bucket and desired blob name
        my_bucket_name = "never-over-bridge-test"
        destination_blob_name = f"deploys/{zip_filename}"

        # Upload the zip file
        upload(my_bucket_name, temp_zip_path, destination_blob_name)
