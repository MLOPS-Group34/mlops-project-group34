import sys
import argparse
from pathlib import Path
from forestfires_project.train import run_training
from forestfires_project.evaluate import run_evaluation
from forestfires_project.visualize import run_visualization

# Add src directory to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))



def main():
    parser = argparse.ArgumentParser(description="Forest Fire Detection Pipeline")
    parser.add_argument("--pipeline", type=str, default="all", choices=["train", "evaluate", "visualize", "all"], help="Choose pipeline stage")
    parser.add_argument("--config", type=str, default="configs/config.yaml", help="Path to config file")
    args = parser.parse_args()

    print(f"Starting pipeline: {args.pipeline}")
    print(f"Config path: {args.config}")

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