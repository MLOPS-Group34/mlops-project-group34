from __future__ import annotations
import os
import socket
import subprocess
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse


def is_running_on_gce() -> bool:
    try:
        with socket.create_connection(("169.254.169.254", 80), timeout=0.2):
            return True
    except OSError:
        pass

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


def sync_gcs_to_local_or_mount(
    gcs_uri: str = "gs://forestfires-data-bucket/data/",
    local_dir: str | Path = "data/",
    mount_dir: str | Path = "/mnt/gcs-bucket",
    mount_only_prefix: bool = True,
) -> Path:

    bucket, prefix = parse_gs_uri(gcs_uri)

    if is_running_on_gce():
        mount_dir = Path(mount_dir)
        mount_dir.mkdir(parents=True, exist_ok=True)

        # If already mounted, just return the correct path
        if _is_mountpoint(mount_dir):
            if mount_only_prefix and prefix:
                return mount_dir.resolve()
            return (mount_dir / prefix).resolve() if prefix else mount_dir.resolve()

        cmd = ["gcsfuse", "--implicit-dirs"]

        # Mount only a subfolder inside the bucket (recommended if you only need that prefix)
        if mount_only_prefix and prefix:
            # gcsfuse expects a dir without trailing slash
            cmd += ["--only-dir", prefix.rstrip("/")]

        # IMPORTANT: bucket name ONLY
        cmd += [bucket, str(mount_dir)]

        print(f">>> STAGE: MOUNT\nRunning: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError as e:
            raise RuntimeError(
                "gcsfuse not found in the container. Install gcsfuse in your Docker image."
            ) from e
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"gcsfuse mount failed with exit code {e.returncode}") from e

        mounted_path = mount_dir.resolve()

        # If we mounted the whole bucket, return the prefix inside it
        if (not mount_only_prefix) and prefix:
            return (mounted_path / prefix).resolve()

        # If we used --only-dir (or no prefix provided), mount_dir itself is the data root
        return mounted_path

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