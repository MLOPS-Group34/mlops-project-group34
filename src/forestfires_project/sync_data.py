from __future__ import annotations

import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse


MOUNT_DIR_DEFAULT = Path("/mnt/gcs-bucket")


def parse_gs_uri(gs_uri: str) -> tuple[str, str]:
    """
    gs://bucket/prefix/... -> (bucket, prefix_with_trailing_slash_or_empty)
    """
    u = urlparse(gs_uri)
    if u.scheme != "gs":
        raise ValueError(f"Expected gs:// URI, got {gs_uri!r}")
    bucket = u.netloc.strip()
    if not bucket:
        raise ValueError(f"Missing bucket in URI: {gs_uri!r}")
    prefix = u.path.lstrip("/")
    if prefix and not prefix.endswith("/"):
        prefix += "/"
    return bucket, prefix


def mount_is_usable(path: Path) -> bool:
    """
    True if mount dir exists, is a mountpoint, and we can list it.
    """
    if not path.exists():
        return False
    if not os.path.ismount(path):
        return False
    try:
        next(path.iterdir())  # try listing at least one entry
    except StopIteration:
        # empty is still usable
        return True
    except PermissionError:
        return False
    except OSError:
        return False
    return True


def sync_gcs_to_local_or_mount(
    gcs_uri: str,
    local_dir: str | Path,
    mount_dir: str | Path = MOUNT_DIR_DEFAULT,
) -> Path:
    """
    If /mnt/gcs-bucket is already mounted and readable, use it.
    Otherwise fall back to gsutil rsync into local_dir (for local dev).

    IMPORTANT:
    - Does NOT run gcsfuse inside the container.
    - Assumes host VM is responsible for gcsfuse mounting when in cloud.
    """
    mount_dir = Path(mount_dir)
    local_dir = Path(local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    bucket, prefix = parse_gs_uri(gcs_uri)

    # 1) Prefer mounted bucket if available
    if mount_is_usable(mount_dir):
        # If the host mounted only-dir=data, then mount_dir already IS "data/"
        # If the host mounted the whole bucket, then we need to append prefix.
        candidate = mount_dir / prefix if prefix else mount_dir
        if candidate.exists():
            return candidate.resolve()
        # If prefix doesn't exist, still return mount_dir (better than failing)
        return mount_dir.resolve()

    # 2) Fallback: local sync using gsutil
    dest = str(local_dir.resolve()) + "/"
    cmd = ["gsutil", "-m", "rsync", "-r", gcs_uri, dest]
    print(f">>> STAGE: SYNC\nRunning: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    return local_dir.resolve()
