import yaml
import os
from pathlib import Path
from loguru import logger
from forestfires_project.data import create_yolo_yaml
from forestfires_project.model import ForestFireYOLO

def run_training(config_path="configs/config.yaml"):
    # Resolve config path relative to project root
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), config_path)
    
    # Load Config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Setup Logging - resolve root_dir from config location
    config_dir = os.path.dirname(config_path)
    root = os.path.abspath(os.path.join(config_dir, config['paths']['root_dir']))
    log_path = os.path.join(root, config['paths']['logs_dir'], "train.log")
    logger.add(log_path, rotation="10 MB")

    # Step 1: Prepare Data
    logger.info("Preparing data configuration...")
    yaml_path = create_yolo_yaml(config, config_path)

    # Step 2: Initialize Model
    model = ForestFireYOLO(config, config_path)

    # Step 3: Train
    model.train(yaml_path)

    # Step 4: Save info
    best_model_path = os.path.join(root, config['paths']['models_dir'], config['project_name'], "weights", "best.pt")
    logger.info(f"Best model saved at: {best_model_path}")

    return best_model_path