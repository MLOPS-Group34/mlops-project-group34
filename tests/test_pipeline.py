import pytest
from unittest import mock


# Test visualize.py
@mock.patch("forestfires_project.visualize.ForestFireYOLO")
@mock.patch("forestfires_project.visualize.get_test_loader")
def test_run_visualization_runs(mock_loader, mock_model):
    """
    Test that run_visualization executes without error using mocks for model and loader.
    Ensures the visualization pipeline can be called with a config and model path.
    """
    from forestfires_project import visualize

    # Mock config and loader
    mock_loader.return_value = []
    mock_model.return_value.load_weights.return_value = None
    mock_model.return_value.predict.return_value = []
    # Should not raise
    try:
        visualize.run_visualization(config_path="configs/config.yaml", model_path=None)
    except Exception as e:
        pytest.fail(f"run_visualization raised {e}")


# Test evaluate.py
@mock.patch("forestfires_project.evaluate.ForestFireYOLO")
@mock.patch("forestfires_project.evaluate.wandb")
def test_run_evaluation_runs(mock_wandb, mock_model):
    """
    Test that run_evaluation executes without error using mocks for model and wandb.
    Ensures evaluation pipeline runs and returns metrics with a valid model path.
    """
    from forestfires_project import evaluate

    mock_model.return_value.load_weights.return_value = None
    mock_model.return_value.model.val.return_value = mock.Mock(box=mock.Mock(map50=0.5, map=0.4, mp=0.9, mr=0.8))
    # Should not raise
    try:
        evaluate.run_evaluation(
            config_path="configs/config.yaml",
            model_path="models/forest_fire_detection/weights/best.pt",
            use_wandb=False,
        )
    except Exception as e:
        pytest.fail(f"run_evaluation raised {e}")


@mock.patch("forestfires_project.evaluate.ForestFireYOLO")
def test_run_evaluation_missing_model(mock_model):
    """
    Test that run_evaluation handles missing model file gracefully (no exception).
    """
    from forestfires_project import evaluate

    # Should not raise, just print error
    try:
        evaluate.run_evaluation(config_path="configs/config.yaml", model_path="/tmp/nonexistent.pt", use_wandb=False)
    except Exception as e:
        pytest.fail(f"run_evaluation (missing model) raised {e}")


# Test train.py
@mock.patch("forestfires_project.train.wandb")
@mock.patch("forestfires_project.train.create_yolo_yaml")
@mock.patch("forestfires_project.train.ForestFireYOLO")
def test_run_training_runs(mock_model, mock_create_yaml, mock_wandb):
    """
    Test that run_training executes without error using mocks for model, yaml creation, and wandb.
    Ensures training pipeline runs and returns a string path to the best model.
    """
    from forestfires_project import train

    mock_create_yaml.return_value = "dummy.yaml"
    mock_model.return_value.train.return_value = None
    # Should not raise
    try:
        result = train.run_training(config_path="configs/config.yaml")
        assert isinstance(result, str)
    except Exception as e:
        pytest.fail(f"run_training raised {e}")
