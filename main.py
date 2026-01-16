import sys
import argparse
from pathlib import Path

from forestfires_project.sync_data import sync_gcs_to_local
from forestfires_project.train import run_training
from forestfires_project.evaluate import run_evaluation
from forestfires_project.visualize import run_visualization


# Add src directory to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


def main():
    parser = argparse.ArgumentParser(description="Forest Fire Detection Pipeline")
    parser.add_argument(
        "--pipeline",
        type=str,
        default="all",
        choices=["sync", "train", "evaluate", "visualize", "all"],
        help="Choose pipeline stage",
    )
    parser.add_argument("--config", type=str, default="configs/config.yaml", help="Path to config file")

    # optional overrides
    parser.add_argument("--gcs_uri", type=str, default="gs://forestfires-data-bucket/data/",
                        help="GCS data prefix (end with /)")
    parser.add_argument("--local_data_dir", type=str, default="data/",
                        help="Local data directory (end with /)")

    args = parser.parse_args()

    print(f"Starting pipeline: {args.pipeline}")
    print(f"Config path: {args.config}")

    # Sync first (so train/eval/vis always see ./data)
    if args.pipeline in ["sync", "all"]:
        sync_gcs_to_local(gcs_uri=args.gcs_uri, local_dir=args.local_data_dir)

    model_path = None

    if args.pipeline in ["train", "all"]:
        print(">>> STAGE: TRAINING")
        model_path = run_training(config_path=args.config)

    if args.pipeline in ["evaluate", "all"]:
        print(">>> STAGE: EVALUATION")
        run_evaluation(config_path=args.config, model_path=model_path)

    if args.pipeline in ["visualize", "all"]:
        print(">>> STAGE: VISUALIZATION")
        run_visualization(config_path=args.config, model_path=model_path)


if __name__ == "__main__":
    main()
