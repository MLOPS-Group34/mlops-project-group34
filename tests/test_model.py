import logging
from src.forestfires_project.model import ForestFireYOLO

logging.basicConfig(level=logging.INFO)


def get_dummy_config():
    return {
        "hyperparameters": {
            "model_type": "yolov8n.pt",  # Use a small model for tests
            "epochs": 1,
            "img_size": 640,
            "batch_size": 1,
            "lr": 0.01,
        },
        "paths": {
            "root_dir": "./",
            "models_dir": "models/forest_fire_detection/weights",
        },
        "project_name": "pytest_project",
    }


def test_model_initialization():
    """Test that ForestFireYOLO initializes with a config and loads YOLO model."""
    config = get_dummy_config()
    logging.info("Initializing ForestFireYOLO model for test.")
    model = ForestFireYOLO(config, config_path="configs/config.yaml")
    logging.info(f"Model initialized with type: {model.model_name}")
    assert hasattr(model, "model"), "Model attribute missing"


def test_load_weights():
    """Test that load_weights replaces the YOLO model instance."""
    config = get_dummy_config()
    model = ForestFireYOLO(config, config_path="configs/config.yaml")
    logging.info("Testing load_weights method.")
    model.load_weights("yolov8n.pt")  # Should not raise
    logging.info("Weights loaded successfully.")
    assert hasattr(model, "model"), "Model attribute missing after loading weights"


def test_predict_output_type():
    """Test that predict returns a result object/list."""
    import numpy as np

    config = get_dummy_config()
    model = ForestFireYOLO(config, config_path="configs/config.yaml")
    dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
    logging.info("Running predict on dummy image.")
    results = model.predict(dummy_img, conf=0.1, save=False)
    logging.info(f"Predict returned type: {type(results)}")
    assert results is not None, "Predict returned None"
