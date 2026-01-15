import yaml
import os
from loguru import logger
from forestfires_project.model import ForestFireYOLO

def run_evaluation(config_path="configs/config.yaml", model_path=None):
    # Resolve config path relative to project root
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), config_path)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Setup root dir - resolve from config location
    config_dir = os.path.dirname(config_path)
    root = os.path.abspath(os.path.join(config_dir, config['paths']['root_dir']))
    
    # If no specific model path provided, try to find the best trained one
    if model_path is None:
        model_path = os.path.join(root, config['paths']['models_dir'], config['project_name'], "weights", "best.pt")

    if not os.path.exists(model_path):
        logger.error(f"Model not found at {model_path}. Please train first.")
        return

    # Initialize and Load
    model_wrapper = ForestFireYOLO(config, config_path)
    model_wrapper.load_weights(model_path)

    logger.info("Starting evaluation on Test set...")
    
    # Ultralytics validation mode on the test split
    # Note: We define 'split=test' to use the test images defined in data.yaml
    metrics = model_wrapper.model.val(split='test', project=os.path.join(root, "reports"), name="eval_results")
    
    # Log relevant metrics
    map50 = metrics.box.map50
    map5095 = metrics.box.map
    p = metrics.box.mp # Mean precision
    r = metrics.box.mr # Mean recall

    logger.info("Evaluation Results:")
    logger.info(f"mAP@50: {map50:.4f}")
    logger.info(f"mAP@50-95: {map5095:.4f}")
    logger.info(f"Precision: {p:.4f}")
    logger.info(f"Recall: {r:.4f}")

    return metrics