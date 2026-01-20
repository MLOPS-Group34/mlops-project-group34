from ultralytics import YOLO
import wandb
import os


class ForestFireYOLO:
    def __init__(self, config, config_path):
        self.config = config
        self.config_path = config_path
        self.model_name = config["hyperparameters"]["model_type"]
        # Load a pretrained YOLO model (n, s, m, l, x)
        print(f"Loading YOLO model: {self.model_name}...")
        try:
            self.model = YOLO(self.model_name)
            print(f"✓ Successfully initialized YOLO model: {self.model_name}")
        except FileNotFoundError:
            print(f"✗ Model {self.model_name} not found. Attempting to download...")
            try:
                # Force download by trying to use the model
                self.model = YOLO(self.model_name)
                print(f"✓ Model downloaded and initialized: {self.model_name}")
            except Exception as e:
                print(f"✗ Failed to download model. Error: {e}")
                print(f"  Please download manually: python -c \"from ultralytics import YOLO; YOLO('{self.model_name}')\"")
                raise
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            raise

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
            patience=hp.get("patience", 10),  # Early stopping threshold
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

    def predict(self, image, class_name=None, save=False):
        """
        Run inference on a single image or batch with class-specific confidence thresholds.
        
        Args:
            image: Input image path or array
            class_name: Optional specific class to filter ("fire" or "smoke")
            save: Whether to save prediction results
        
        Returns:
            Predictions filtered by appropriate confidence threshold
        """
        hp = self.config["hyperparameters"]
        
        # Get class-specific confidence threshold
        if class_name == "fire":
            conf = hp.get("fire_confidence", 0.5)
        elif class_name == "smoke":
            conf = hp.get("smoke_confidence", 0.75)
        else:
            # Default: use fire_confidence as base
            conf = hp.get("fire_confidence", 0.5)
        
        return self.model.predict(image, conf=conf, verbose=False, save=save)

    def load_weights(self, weights_path):
        """Load specific weights (e.g., best.pt)"""
        print(f"Loading weights from {weights_path}")
        self.model = YOLO(weights_path)
