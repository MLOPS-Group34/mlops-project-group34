# forestfires_project

Hybrid Fire and Smoke Detection with MLOPS Practices

This project is made by group 34 for the MLOPS January course (02476)

The goal of the project is to design, implement and evaluate a reproducible machine learning pipeline for image-based fire and smoke detection applying the MLOps practices presented throughout the course. The aim is to achieve a well-structured project that focuses on deploying, testing and monitoring a YOLOv8 detection system in a robust and maintainable way that allows for multiple collaborators.

The project uses **YOLOv8** for spatial detection of fire and smoke in images. The framework is built with PyTorch and Ultralytics YOLO, with Docker for environment reproducibility and YAML configuration files for experiment management. Dependency management is handled via `uv` and `pyproject.toml` to ensure consistent and traceable builds.

## Quick Start

### Prerequisites
- Python 3.11+
- `uv` package manager installed
- Fire and smoke dataset in `data/processed/` (train/val/test splits)

### Running the Pipeline

1. **Configure your experiment** in `configs/config.yaml`:
   - Set `data_sampling.enabled: true` for quick testing with subset of data
   - Adjust `train_samples`, `val_samples`, `test_samples` for dataset size
   - Set `epochs` and `batch_size` based on your hardware
   - For quick testing, use `configs/config_quick_test.yaml`

2. **Run the complete pipeline** from the project root:
   ```bash
   uv run python main.py --pipeline all --config configs/config.yaml
   ```

3. **Run individual stages**:
   ```bash
   # Cloud data synchronization only
   main.py --pipeline sync
   
   # Training only
   uv run python main.py --pipeline train --config configs/config.yaml
   
   # Evaluation only
   uv run python main.py --pipeline evaluate --config configs/config.yaml
   
   # Visualization only
   uv run python main.py --pipeline visualize --config configs/config.yaml
   ```
### Configuration Guide

Edit `configs/config.yaml` to customize your training:

```yaml
# Data Sampling - Control dataset size
data_sampling:
  enabled: true          # Set false to use all data
  train_samples: 100     # Number of training images (null = all)
  val_samples: 30        # Number of validation images
  test_samples: 20       # Number of test images
  random_seed: 42        # For reproducible sampling

# Training Hyperparameters
hyperparameters:
  model_type: "yolov8n.pt"  # Options: yolov8n/s/m/l/x.pt
  epochs: 50                # Training epochs
  batch_size: 32            # Batch size
  img_size: 640             # Image size
  lr: 0.01                  # Learning rate
```

**Recommended configurations:**
- **Quick test**: 100 train samples, 5 epochs (~5 min)
- **Small experiment**: 500 train samples, 50 epochs (~1 hour)
- **Good performance**: 2000 train samples, 100 epochs (~3 hours)
- **Production**: All data, 150-200 epochs (~12-24 hours)
 


## Project structure

The directory structure of the project looks like this:
```txt
├── .github/                  # Github actions and dependabot
│   ├── dependabot.yaml
│   ├── agents/               # AI agent configurations
│   ├── prompts/              # Prompt templates
│   └── workflows/
│       ├── tests.yaml
│       ├── linting.yaml
│       └── pre-commit-update.yaml
├── configs/                  # Configuration files
│   ├── config.yaml           # Main training configuration
│   └── config_quick_test.yaml  # Quick test configuration
├── data/                     # Data directory
│   ├── processed/            # Train/val/test splits
│   │   ├── train/
│   │   │   ├── images/       # Training images (gitignored)
│   │   │   └── labels/       # YOLO format labels (gitignored)
│   │   ├── val/              # Validation data
│   │   └── test/             # Test data
│   ├── raw/                  # Original raw data
│   ├── samples/              # Sample data for testing
│   └── final/                # Final processed datasets
├── dockerfiles/              # Dockerfiles
│   ├── api.dockerfile
│   └── train.dockerfile
├── docs/                     # Documentation
│   ├── mkdocs.yaml
│   ├── README.md
│   └── source/
│       └── index.md
├── logs/                     # Training and pipeline logs
├── models/                   # Trained models and weights
│   └── forest_fire_detection/
│       └── weights/
│           └── best.pt       # Best model checkpoint
├── notebooks/                # Jupyter notebooks
│   ├── data_exploration.ipynb
│   └── generate_samples.ipynb
├── reports/                  # Reports and visualizations
│   └── figures/
├── src/                      # Source code
│   └── forestfires_project/
│       ├── __init__.py
│       ├── api.py            # API endpoints
│       ├── data.py           # Data loading and sampling
│       ├── evaluate.py       # Model evaluation
│       ├── model.py          # YOLOv8 model wrapper
│       ├── train.py          # Training pipeline
│       ├── utils.py          # Utility functions
│       └── visualize.py      # Visualization pipeline
├── tests/                    # Tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_data.py
│   └── test_model.py
├── .devcontainer/            # VS Code dev container config
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── LICENSE
├── main.py                   # Main pipeline entry point
├── pyproject.toml            # Python project file
├── README.md                 # Project README
└── tasks.py                  # Project tasks
```


Created using [mlops_template](https://github.com/SkafteNicki/mlops_template),
a [cookiecutter template](https://github.com/cookiecutter/cookiecutter) for getting
started with Machine Learning Operations (MLOps).
