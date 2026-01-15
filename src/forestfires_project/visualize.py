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
    
    # Convert class dict to list in correct order
    classes_dict = config['hyperparameters']['classes']
    class_names = [classes_dict[i] for i in sorted(classes_dict.keys())]

    # Collect predictions for all images to find most confident ones
    logger.info("Running inference on test set to find most confident predictions...")
    all_results = []
    
    for batch_idx, (images, gt_boxes_batch, img_paths) in enumerate(loader):
        results = model_wrapper.predict(list(images))
        
        for i, result in enumerate(results):
            pred_boxes = result.boxes.data.cpu().numpy()
            # Calculate average confidence for this image
            avg_conf = pred_boxes[:, 4].mean() if len(pred_boxes) > 0 else 0.0
            max_conf = pred_boxes[:, 4].max() if len(pred_boxes) > 0 else 0.0
            
            all_results.append({
                'image': images[i],
                'gt_boxes': gt_boxes_batch[i],
                'pred_boxes': pred_boxes,
                'avg_conf': avg_conf,
                'max_conf': max_conf,
                'num_detections': len(pred_boxes)
            })
    
    # Sort by average confidence and get top 6
    all_results.sort(key=lambda x: x['avg_conf'], reverse=True)
    top_6 = all_results[:6]
    
    conf_scores = [f"{r['avg_conf']:.3f}" for r in top_6]
    logger.info(f"Selected top 6 images with confidence scores: {conf_scores}")

    # Plotting
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    axes = axes.flatten()

    for i, result_data in enumerate(top_6):
        # Prepare GT Image
        img_gt = draw_boxes(result_data['image'], result_data['gt_boxes'], 
                           color=(0, 255, 0), label_names=class_names, is_pred=False)
        
        # Draw predictions in Red on top of the GT image
        img_final = draw_boxes(img_gt, result_data['pred_boxes'], 
                              color=(0, 0, 255), label_names=class_names, is_pred=True)

        axes[i].imshow(img_final)
        axes[i].set_title(f"Image {i+1}: Avg Conf={result_data['avg_conf']:.3f}\nGT(Green) vs Pred(Red)")
        axes[i].axis('off')

    output_path = os.path.join(save_dir, "predictions_grid.png")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    
    logger.success(f"Visualization saved to {output_path}")