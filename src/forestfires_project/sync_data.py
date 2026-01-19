# forestfires_project/sync_data.py
from __future__ import annotations

import subprocess
from pathlib import Path


def sync_gcs_to_local(
    gcs_uri: str = "gs://forestfires-data-bucket/data/",
    local_dir: str | Path = "data/",
) -> Path:
    if not gcs_uri.endswith("/"):
        gcs_uri += "/"
    local_dir = Path(local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    cmd = ["gsutil", "-m", "rsync", "-r", gcs_uri, str(local_dir) + "/"]

    print(f">>> STAGE: SYNC\nRunning: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError as e:
        raise RuntimeError("gsutil not found. Install Google Cloud SDK or include it in your Docker image.") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"gsutil rsync failed with exit code {e.returncode}") from e

    print(f"Sync complete. Local data dir: {local_dir.resolve()}")
    return local_dir.resolve()
