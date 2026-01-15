from ultralytics import YOLO
import wandb
import os


class ForestFireYOLO:
    def __init__(self, config, config_path):
        self.config = config
        self.config_path = config_path
        self.model_name = config["hyperparameters"]["model_type"]
        # Load a pretrained YOLO model (n, s, m, l, x)
        self.model = YOLO(self.model_name)
        print(f"Initialized YOLO model: {self.model_name}")

    def train(self, data_yaml_path):
        """Wrapper for the YOLO training loop with wandb integration"""
        hp = self.config["hyperparameters"]
        # Resolve root from config file location
        config_dir = os.path.dirname(self.config_path)
        root = os.path.abspath(os.path.join(config_dir, self.config["paths"]["root_dir"]))
        project_path = os.path.join(root, self.config["paths"]["models_dir"])

        print("Starting training...")
        # Ultralytics YOLO has built-in wandb integration
        # It will automatically log metrics when wandb is initialized
        # Set device to allow YOLO to use available GPU/CPU
        results = self.model.train(
            data=data_yaml_path,
            epochs=hp["epochs"],
            imgsz=hp["img_size"],
            batch=hp["batch_size"],
            lr0=hp["lr"],
            project=project_path,
            name=self.config["project_name"],
            exist_ok=True,
            verbose=True,
            save=True,  # Keep weights only
            plots=False,  # No training plots
            save_txt=False,  # No txt files
            save_conf=False,  # No confidence files
            save_crop=False,  # No crop predictions
        )

        # Log final training metrics to wandb
        if results:
            # Extract key metrics from results
            results_dict = results.results_dict

            final_metrics = {
                "final/mAP50": results_dict.get("metrics/mAP50(B)", 0),
                "final/mAP50-95": results_dict.get("metrics/mAP50-95(B)", 0),
                "final/precision": results_dict.get("metrics/precision(B)", 0),
                "final/recall": results_dict.get("metrics/recall(B)", 0),
                "final/box_loss": results_dict.get("train/box_loss", 0),
                "final/cls_loss": results_dict.get("train/cls_loss", 0),
            }
            wandb.log(final_metrics)

            print("Training metrics logged to wandb:")

        print("Training completed.")
        return results

    def predict(self, image, conf=0.25, save=False):
        """Run inference on a single image or batch"""
        return self.model.predict(image, conf=conf, verbose=False, save=save)

    def load_weights(self, weights_path):
        """Load specific weights (e.g., best.pt)"""
        print(f"Loading weights from {weights_path}")
        self.model = YOLO(weights_path)
