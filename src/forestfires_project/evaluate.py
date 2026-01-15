import yaml
import os
import wandb
from dotenv import load_dotenv
from forestfires_project.model import ForestFireYOLO

def run_evaluation(config_path="configs/config.yaml", model_path=None, use_wandb=True):
    # Load environment variables
    load_dotenv()
    
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
        print(f"Model not found at {model_path}. Please train first.")
        return

    # Initialize wandb if requested
    if use_wandb:
        wandb.init(
            project=config['wandb_project'],
            name=f"{config['project_name']}_evaluation",
            config=config,
            job_type="evaluation",
            settings=wandb.Settings(system_sample_rate=0)  # Disable system metrics logging
        )

    # Initialize and Load
    model_wrapper = ForestFireYOLO(config, config_path)
    model_wrapper.load_weights(model_path)

    print("Starting evaluation on Test set...")
    
    # Ultralytics validation mode on the test split
    # Disable all local file outputs - metrics go to wandb
    metrics = model_wrapper.model.val(
        split='test',
        plots=False,  # No confusion matrix plots
        save_txt=False,  # No results txt
        save_conf=False,  # No confidence files
        save_crop=False  # No crop predictions
    )
    
    # Log relevant metrics
    map50 = metrics.box.map50
    map5095 = metrics.box.map
    p = metrics.box.mp # Mean precision
    r = metrics.box.mr # Mean recall

    print("Evaluation Results:")
    print(f"mAP@50: {map50:.4f}")
    print(f"mAP@50-95: {map5095:.4f}")
    print(f"Precision: {p:.4f}")
    print(f"Recall: {r:.4f}")
    
    # Log to wandb
    if use_wandb:
        eval_metrics = {
            'eval/mAP50': map50,
            'eval/mAP50-95': map5095,
            'eval/precision': p,
            'eval/recall': r
        }
        wandb.log(eval_metrics)
        wandb.finish()

    return metrics