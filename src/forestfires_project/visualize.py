import matplotlib.pyplot as plt
import cv2
import yaml
import os
from forestfires_project.data import get_test_loader
from forestfires_project.model import ForestFireYOLO


def draw_boxes(img, boxes, color=(0, 255, 0), label_names=None, is_pred=False):
    """Helper to draw boxes on image.
    boxes format: [x1, y1, x2, y2, class_id] (for GT)
                  [x1, y1, x2, y2, conf, class_id] (for Pred)
    Note: color is in RGB format for matplotlib compatibility
    """
    img_copy = img.copy()
    for box in boxes:
        if is_pred:
            x1, y1, x2, y2, conf, cls = box
            label = f"{label_names[int(cls)]} {conf:.2f}"
        else:
            x1, y1, x2, y2, cls = box
            label = f"{label_names[int(cls)]}"

        # Draw rectangle and text in RGB color format
        import matplotlib.patches as mpatches
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        import numpy as np
        
        # For RGB images (matplotlib), we can draw directly with RGB colors
        # Using a simple approach: overlay colored rectangles
        cv2.rectangle(img_copy, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(img_copy, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return img_copy


def run_visualization(config_path="configs/config.yaml", model_path=None):
    # Resolve config path relative to project root
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), config_path)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Setup root dir - resolve from config location
    config_dir = os.path.dirname(config_path)
    root = os.path.abspath(os.path.join(config_dir, config["paths"]["root_dir"]))
    save_dir = os.path.join(root, config["paths"]["reports_dir"])
    os.makedirs(save_dir, exist_ok=True)

    if model_path is None:
        model_path = os.path.join(root, config["paths"]["models_dir"], config["project_name"], "weights", "best.pt")

    # Load Model and Data
    model_wrapper = ForestFireYOLO(config, config_path)
    model_wrapper.load_weights(model_path)
    loader = get_test_loader(config, config_path)

    # Convert class dict to list in correct order
    classes_dict = config["hyperparameters"]["classes"]
    class_names = [classes_dict[i] for i in sorted(classes_dict.keys())]
    print(f"Classes: {class_names}")

    # Collect predictions for all images to find most confident ones
    print("Running inference on test set to find most confident predictions...")
    all_results = []
    
    # Debug counters
    total_gt_boxes = 0
    total_images_with_gt = 0

    for batch_idx, (images, gt_boxes_batch, img_paths) in enumerate(loader):
        # Convert tensor images to numpy for YOLO inference
        # Use conf threshold to filter predictions
        results = model_wrapper.predict(images, conf=0.3, draw_boxes=False)

        for i, result in enumerate(results):
            # Extract predictions with confidence and class info
            # Format: [x1, y1, x2, y2, conf, class_id]
            pred_boxes_raw = result.boxes.data.cpu().numpy() if result.boxes is not None else []

            # Restructure: keep only boxes with format [x1, y1, x2, y2, conf, class_id]
            pred_boxes = pred_boxes_raw[:, :6] if len(pred_boxes_raw) > 0 else []

            # Debug: show raw prediction counts
            if batch_idx == 0 and i == 0:
                print(f"[DEBUG] First batch: {len(pred_boxes)} boxes detected (conf threshold 0.3)")
                if len(pred_boxes) > 0:
                    print(f"[DEBUG] Sample box: {pred_boxes[0]} (conf={pred_boxes[0][4]:.4f})")

            # Calculate average confidence for this image
            avg_conf = pred_boxes[:, 4].mean() if len(pred_boxes) > 0 else 0.0
            max_conf = pred_boxes[:, 4].max() if len(pred_boxes) > 0 else 0.0
            
            # Validate ground truth boxes
            gt_boxes = gt_boxes_batch[i]
            if len(gt_boxes) > 0:
                total_images_with_gt += 1
                total_gt_boxes += len(gt_boxes)
                # Verify GT box format: [x1, y1, x2, y2, cls]
                if batch_idx == 0 and i == 0 and len(gt_boxes) > 0:
                    print(f"[DEBUG] Sample GT box: {gt_boxes[0]} (format: [x1, y1, x2, y2, class_id])")

            all_results.append(
                {
                    "image": images[i],
                    "gt_boxes": gt_boxes,
                    "pred_boxes": pred_boxes,
                    "avg_conf": avg_conf,
                    "max_conf": max_conf,
                    "num_detections": len(pred_boxes),
                }
            )

    # Sort by average confidence and get top 24 (4 grids of 6)
    all_results.sort(key=lambda x: x["avg_conf"], reverse=True)
    top_24 = all_results[:24]

    conf_scores = [f"{r['avg_conf']:.3f}" for r in top_24]
    print(f"\nGround Truth Stats: {total_images_with_gt} images with GT, {total_gt_boxes} total GT boxes")
    print(f"Selected top 24 images with confidence scores: {conf_scores}")

    # Create 4 separate grid files (6 images each)
    for grid_idx in range(4):
        start_idx = grid_idx * 6
        end_idx = start_idx + 6
        grid_images = top_24[start_idx:end_idx]

        # Skip if we don't have enough images for this grid
        if len(grid_images) == 0:
            break

        # Plotting
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        axes = axes.flatten()

        for i, result_data in enumerate(grid_images):
            # Prepare GT Image
            img_gt = draw_boxes(
                result_data["image"], result_data["gt_boxes"], color=(0, 255, 0), label_names=class_names, is_pred=False
            )

            # Draw predictions in Red (RGB format) on top of the GT image
            img_final = draw_boxes(
                img_gt, result_data["pred_boxes"], color=(255, 0, 0), label_names=class_names, is_pred=True
            )

            axes[i].imshow(img_final)
            axes[i].set_title(
                f"Image {start_idx + i + 1}: Avg Conf={result_data['avg_conf']:.3f}\nGT(Green) vs Pred(Red)"
            )
            axes[i].axis("off")

        # Hide unused subplots if we have fewer than 6 images in this grid
        for j in range(len(grid_images), 6):
            axes[j].axis("off")

        output_path = os.path.join(save_dir, f"predictions_grid_{grid_idx + 1}.png")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

        print(f"Visualization {grid_idx + 1}/4 saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Visualize forest fire detection predictions")
    parser.add_argument("--config", type=str, default="configs/config.yaml", help="Path to config file")
    parser.add_argument(
        "--model_path", type=str, default=None, help="Path to model weights (optional, uses best.pt if not provided)"
    )
    args = parser.parse_args()

    run_visualization(config_path=args.config, model_path=args.model_path)
