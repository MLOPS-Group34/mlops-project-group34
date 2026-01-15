import matplotlib.pyplot as plt
import cv2
import yaml
import os
import numpy as np
from loguru import logger
from forestfires_project.data import get_test_loader
from forestfires_project.model import ForestFireYOLO

def draw_boxes(img, boxes, color=(0, 255, 0), label_names=None, is_pred=False):
    """Helper to draw boxes on image. 
    boxes format: [x1, y1, x2, y2, class_id] (for GT)
                  [x1, y1, x2, y2, conf, class_id] (for Pred)
    """
    img_copy = img.copy()
    for box in boxes:
        if is_pred:
            x1, y1, x2, y2, conf, cls = box
            label = f"{label_names[int(cls)]} {conf:.2f}"
        else:
            x1, y1, x2, y2, cls = box
            label = f"{label_names[int(cls)]}"
            
        cv2.rectangle(img_copy, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(img_copy, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return img_copy

def run_visualization(config_path="configs/config.yaml", model_path=None):
    # Resolve config path relative to project root
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), config_path)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Setup root dir - resolve from config location    
    config_dir = os.path.dirname(config_path)
    root = os.path.abspath(os.path.join(config_dir, config['paths']['root_dir']))
    save_dir = os.path.join(root, config['paths']['reports_dir'])
    os.makedirs(save_dir, exist_ok=True)
    
    if model_path is None:
        model_path = os.path.join(root, config['paths']['models_dir'], config['project_name'], "weights", "best.pt")

    # Load Model and Data
    model_wrapper = ForestFireYOLO(config, config_path)
    model_wrapper.load_weights(model_path)
    loader = get_test_loader(config, config_path)
    class_names = config['hyperparameters']['classes']

    # Get one batch (batch size set to 6 in data.py)
    images, gt_boxes_batch, _ = next(iter(loader))
    
    # Run Inference
    results = model_wrapper.predict(list(images)) # Pass list of numpy arrays

    # Plotting
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()

    for i in range(6):
        if i >= len(images): break
        
        # Prepare GT Image
        img_gt = draw_boxes(images[i], gt_boxes_batch[i], color=(0, 255, 0), label_names=class_names, is_pred=False)
        
        # Prepare Pred Image (Process results from YOLO)
        pred_boxes = results[i].boxes.data.cpu().numpy() # x1, y1, x2, y2, conf, cls
        # We draw predictions in Red on top of the GT image to see both, or just Red?
        # Let's draw Red (Pred) on the GT image to see overlap
        img_final = draw_boxes(img_gt, pred_boxes, color=(0, 0, 255), label_names=class_names, is_pred=True)

        axes[i].imshow(img_final)
        axes[i].set_title(f"Image {i+1}: GT(Green) vs Pred(Red)")
        axes[i].axis('off')

    output_path = os.path.join(save_dir, "predictions_grid.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    logger.success(f"Visualization saved to {output_path}")