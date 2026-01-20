from __future__ import annotations

import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_MOUNT_DIR = Path("/mnt/gcs-bucket")


def parse_gs_uri(gs_uri: str) -> tuple[str, str]:
    """
    Parse GCS URI:
      gs://bucket
      gs://bucket/
      gs://bucket/data
      gs://bucket/data/

    Returns (bucket, prefix) where prefix has trailing slash or is "".
    """
    u = urlparse(gs_uri)
    if u.scheme != "gs":
        raise ValueError(f"Expected gs:// URI, got: {gs_uri!r}")

    bucket = u.netloc.strip()
    if not bucket:
        raise ValueError(f"Missing bucket name in: {gs_uri!r}")

    prefix = u.path.lstrip("/")  # may be ""
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    return bucket, prefix


def is_readable_mount(path: Path) -> bool:
    """
    True if:
      - path exists
      - and it's a mountpoint
      - and the current user can list it (no PermissionError)
    """
    if not path.exists():
        return False
    if not os.path.ismount(path):
        return False

    try:
        # Try listing. This will throw PermissionError if inaccessible.
        _ = next(path.iterdir(), None)
        return True
    except PermissionError:
        return False
    except OSError:
        return False


def sync_gcs_to_local_or_mount(
    gcs_uri: str,
    local_dir: str | Path,
    mount_dir: str | Path = DEFAULT_MOUNT_DIR,
) -> Path:
    """
    Cloud/VM workflow (recommended):
      - GCS bucket is mounted on the VM host at /mnt/gcs-bucket (via gcsfuse)
      - Docker bind-mounts that into container: -v /mnt/gcs-bucket:/mnt/gcs-bucket
      - This function MUST NOT run gcsfuse inside the container.

    Local workflow:
      - If no readable mount exists, fallback to: gsutil -m rsync -r gs://... local_dir

    Returns a Path to data directory.
    """
    mount_dir = Path(mount_dir)
    local_dir = Path(local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    bucket, prefix = parse_gs_uri(gcs_uri)

    # 1) Prefer host-mounted path if available
    if is_readable_mount(mount_dir):
        # Two possibilities:
        # A) Host mounted only-dir=data -> mount_dir already points to the dataset root
        # B) Host mounted whole bucket -> data is under mount_dir/prefix
        candidate = (mount_dir / prefix) if prefix else mount_dir

        # If host mounted only-dir=data and prefix=="data/", then candidate becomes mount_dir/"data/"
        # That won't exist, so handle that:
        if not candidate.exists() and prefix:
            # If prefix is like "data/", and mount_dir already IS that folder, use mount_dir
            if prefix.rstrip("/") in ("data",):
                return mount_dir.resolve()

        return candidate.resolve() if candidate.exists() else mount_dir.resolve()

    # 2) Fallback: local sync using gsutil (for dev/laptop)
    cmd = ["gsutil", "-m", "rsync", "-r", gcs_uri, str(local_dir.resolve()) + "/"]
    print(f">>> STAGE: SYNC\nRunning: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as e:
        raise RuntimeError(
            "gsutil not found in container. Either install Google Cloud SDK (gsutil) "
            "or run with a host-mounted /mnt/gcs-bucket."
        ) from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"gsutil rsync failed with exit code {e.returncode}") from e

    return local_dir.resolve()
