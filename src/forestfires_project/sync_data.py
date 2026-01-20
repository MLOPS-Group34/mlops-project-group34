def is_running_on_gce():
    """Check if the code is running on a Google Cloud Compute Engine instance."""
    try:
        product_name_path = "/sys/class/dmi/id/product_name"
        if os.path.exists(product_name_path):
            with open(product_name_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "Google" in content or "Google Compute Engine" in content:
                return True
    except OSError:
        pass

    return False


def parse_gs_uri(gs_uri: str) -> Tuple[str, str]:
    """
    Parse a GCS URI like:
      gs://bucket
      gs://bucket/
      gs://bucket/data
      gs://bucket/data/

    Returns: (bucket, prefix)
      bucket: "bucket"
      prefix: "" or "data/" or "some/path/"
    """
    u = urlparse(gs_uri)
    if u.scheme != "gs":
        raise ValueError(f"Expected a gs:// URI, got: {gs_uri!r}")

    bucket = u.netloc.strip()
    if not bucket:
        raise ValueError(f"Missing bucket in gs:// URI: {gs_uri!r}")

    prefix = u.path.lstrip("/")  # may be "" or "data/" or "data"
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    return bucket, prefix


def _is_mountpoint(path: Path) -> bool:
    """
    Check if a path is a mountpoint (Linux).
    """
    try:
        return os.path.ismount(path)
    except OSError:
        return False

    # 2) Fall back to DMI product_name (works on many VMs)
    try:
        product_name_path = "/sys/class/dmi/id/product_name"
        if os.path.exists(product_name_path):
            with open(product_name_path, "r", encoding="utf-8") as f:
                content = f.read()
            if "Google" in content or "Google Compute Engine" in content:
                return True
    except OSError:
        pass

    return False


def parse_gs_uri(gs_uri: str) -> Tuple[str, str]:
    """
    Parse a GCS URI like:
      gs://bucket
      gs://bucket/
      gs://bucket/data
      gs://bucket/data/

    Returns: (bucket, prefix)
      bucket: "bucket"
      prefix: "" or "data/" or "some/path/"
    """
    u = urlparse(gs_uri)
    if u.scheme != "gs":
        raise ValueError(f"Expected a gs:// URI, got: {gs_uri!r}")

    bucket = u.netloc.strip()
    if not bucket:
        raise ValueError(f"Missing bucket in gs:// URI: {gs_uri!r}")

    prefix = u.path.lstrip("/")  # may be "" or "data/" or "data"
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    return bucket, prefix


def _is_mountpoint(path: Path) -> bool:
    """
    Check if a path is a mountpoint (Linux).
    """
    try:
        return os.path.ismount(path)
    except OSError:
        return False


from pathlib import Path
import subprocess

def sync_gcs_to_local_or_mount(
    gcs_uri: str = "gs://forestfires-data-bucket/data/",
    local_dir: str | Path = "data/",
    mount_dir: str | Path = "/mnt/gcs-bucket",
    mount_only_prefix: bool = True,
) -> Path:

    if not gcs_uri.endswith("/"):
        gcs_uri += "/"

    if is_running_on_gce():
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

        print(f"Bucket mounted at: {mount_dir.resolve()}")
        return mount_dir.resolve()
    else:
        local_dir = Path(local_dir)
        local_dir.mkdir(parents=True, exist_ok=True)

        # IMPORTANT: bucket name ONLY
        cmd += [bucket, str(mount_dir)]

        print(f">>> STAGE: MOUNT\nRunning: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError as e:
            raise RuntimeError("gsutil not found. Install Google Cloud SDK or include it in your Docker image.") from e
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"gsutil rsync failed with exit code {e.returncode}") from e

    # Local execution: sync from gs:// to local folder
    local_dir = Path(local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    # Ensure trailing slash semantics for rsync destination
    dest = str(local_dir.resolve()) + "/"

    cmd = ["gsutil", "-m", "rsync", "-r", gcs_uri, dest]
    print(f">>> STAGE: SYNC\nRunning: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        return local_dir.resolve()
    except FileNotFoundError as e:
        raise RuntimeError(
            "gsutil not found. Install Google Cloud SDK (gsutil) or include it in your Docker image."
        ) from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"gsutil rsync failed with exit code {e.returncode}") from e
