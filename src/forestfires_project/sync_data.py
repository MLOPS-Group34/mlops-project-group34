def is_running_on_gce():
    """Check if the code is running on a Google Cloud Compute Engine instance."""
    try:
        with open("/sys/class/dmi/id/product_name", "r") as f:
            print("Checking GCE environment...")
            return "Google" in f.read()
            print("GCE environment detected.")
    except FileNotFoundError:
        print("Not running on GCE.")
        return False

def is_running_on_gce():
    """Check if the code is running on a Google Cloud Compute Engine instance."""
    try:
        with open("/sys/class/dmi/id/product_name", "r") as f:
            print("Checking GCE environment...")
            return "Google" in f.read()
            print("GCE environment detected.")
    except FileNotFoundError:
        print("Not running on GCE.")
        return False


from pathlib import Path
import subprocess

def sync_gcs_to_local_or_mount(
    gcs_uri: str = "gs://forestfires-data-bucket/data/",
    local_dir: str | Path = "data/",
    mount_dir: str | Path = "/mnt/gcs-bucket",
) -> Path:

    if not gcs_uri.endswith("/"):
        gcs_uri += "/"

    if is_running_on_gce():
        # Mount the bucket using gcsfuse
        mount_dir = Path(mount_dir)
        mount_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "gcsfuse",
            "--implicit-dirs",
            "forestfires-data-bucket",  # Only the bucket name
            str(mount_dir),
        ]
        print(f">>> STAGE: MOUNT\nRunning: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True)
            print(f"Bucket mounted at: {mount_dir.resolve()}")
            return mount_dir.resolve()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"gcsfuse mount failed with exit code {e.returncode}") from e
    else:
        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)

        cmd = ["gsutil", "-m", "rsync", "-r", gcs_uri, str(local_dir) + "/"]
        print(f">>> STAGE: SYNC\nRunning: {' '.join(cmd)}")

        try:
            subprocess.run(cmd, check=True)
            print(f"Sync complete. Local data dir: {local_dir.resolve()}")
            return local_dir.resolve()
        except FileNotFoundError:
            raise RuntimeError("gsutil not found. Install Google Cloud SDK or include it in your Docker image.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"gsutil rsync failed with exit code {e.returncode}") from e