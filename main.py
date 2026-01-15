import sys
import os
import argparse
from pathlib import Path
from loguru import logger

# Add src directory to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

from forestfires_project.train import run_training
from forestfires_project.evaluate import run_evaluation
from forestfires_project.visualize import run_visualization

def main():
    parser = argparse.ArgumentParser(description="Forest Fire Detection Pipeline")
    parser.add_argument("--pipeline", type=str, default="all", choices=["train", "evaluate", "visualize", "all"], help="Choose pipeline stage")
    parser.add_argument("--config", type=str, default="configs/config.yaml", help="Path to config file")
    args = parser.parse_args()

    # Ensure logs directory exists
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logger.add(str(log_dir / "pipeline.log"), rotation="10 MB")
    logger.info(f"Starting pipeline: {args.pipeline}")
    logger.info(f"Config path: {args.config}")

    model_path = None

    if args.pipeline in ["train", "all"]:
        logger.info(">>> STAGE: TRAINING")
        model_path = run_training(config_path=args.config)

    if args.pipeline in ["evaluate", "all"]:
        logger.info(">>> STAGE: EVALUATION")
        run_evaluation(config_path=args.config, model_path=model_path)

    if args.pipeline in ["visualize", "all"]:
        logger.info(">>> STAGE: VISUALIZATION")
        run_visualization(config_path=args.config, model_path=model_path)

if __name__ == "__main__":
    main()