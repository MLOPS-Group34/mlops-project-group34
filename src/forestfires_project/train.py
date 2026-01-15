import yaml
import os
from pathlib import Path
import wandb
from dotenv import load_dotenv
from forestfires_project.data import create_yolo_yaml
from forestfires_project.model import ForestFireYOLO

def run_training(config_path="configs/config.yaml"):
    # Load environment variables (including WANDB_API_KEY)
    load_dotenv()
    
    # Resolve config path relative to project root
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), config_path)
    
    # Load Config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Initialize wandb
    config_dir = os.path.dirname(config_path)
    root = os.path.abspath(os.path.join(config_dir, config['paths']['root_dir']))
    
    wandb.init(
        project=config['wandb_project'],
        name=config['project_name'],
        config=config
    )

    # Step 1: Prepare Data
    print("Preparing data configuration...")
    yaml_path = create_yolo_yaml(config, config_path)

    # Step 2: Initialize Model
    model = ForestFireYOLO(config, config_path)

    # Step 3: Train
    model.train(yaml_path)

    # Step 4: Save info
    best_model_path = os.path.join(root, config['paths']['models_dir'], config['project_name'], "weights", "best.pt")
    print(f"Best model saved at: {best_model_path}")
    
    wandb.finish()

    return best_model_path