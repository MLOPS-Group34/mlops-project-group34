from ultralytics import YOLO
from loguru import logger
import os

class ForestFireYOLO:
    def __init__(self, config, config_path):
        self.config = config
        self.config_path = config_path
        self.model_name = config['hyperparameters']['model_type']
        # Load a pretrained YOLO model (n, s, m, l, x)
        self.model = YOLO(self.model_name) 
        logger.info(f"Initialized YOLO model: {self.model_name}")

    def train(self, data_yaml_path):
        """Wrapper for the YOLO training loop"""
        hp = self.config['hyperparameters']
        # Resolve root from config file location
        config_dir = os.path.dirname(self.config_path)
        root = os.path.abspath(os.path.join(config_dir, self.config['paths']['root_dir']))
        project_path = os.path.join(root, self.config['paths']['models_dir'])

        logger.info("Starting training...")
        results = self.model.train(
            data=data_yaml_path,
            epochs=hp['epochs'],
            imgsz=hp['img_size'],
            batch=hp['batch_size'],
            lr0=hp['lr'],
            project=project_path,
            name=self.config['project_name'],
            exist_ok=True, # Overwrite if exists
            verbose=True
        )
        logger.success("Training completed.")
        return results

    def predict(self, image, conf=0.25):
        """Run inference on a single image or batch"""
        return self.model.predict(image, conf=conf, verbose=False)

    def load_weights(self, weights_path):
        """Load specific weights (e.g., best.pt)"""
        logger.info(f"Loading weights from {weights_path}")
        self.model = YOLO(weights_path)