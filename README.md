# forestfires_project

Hybrid Fire and Smoke Detection with MLOPS Practices
This project is made by group 34 for the MLOPS January course (02476)

The goal of the project is to design, implement and evaluate a reproducible machine learning pipeline for video-based fire and smoke detection applying the MLOps practices presented throughout the course. The aim is achieve a well-structured project that focuses on deploying, testing and monitoring an existing hybrid detection system in a robust and maintainable way that allows for multiple collaborators. This is to simulate a real-world project where machine learning engineers, data scientists, software developers and other relevant actors can coorporate on the same project rather individual projects. 

The project is based on an existing hybrid fire detection framework built by Github user pedbrgs that combines spatial and temporal analysis. The scope of the project is subject to change throughout the course, however the current framework consists of two stages: 
In the first stage, a YOLOv5 object detection model identifies candidate fire or smoke regions in individual video frames. In the second stage, temporal verification techniques such as the Area Variation Technique or the Temporal Persistence Technique are applied to confirm whether a true fire event is occurring over time. For comparison, baseline convolutional neural network models such as FireNet and MobileNet based classifiers will also be evaluated.

The priimary framework used in the project is PyTorch along with YOLOv5 for sptial detection and OpenCV for temporal analysis and tracking. Docker is used to ensure environment reproducibility, and hydra to manage configurate files. Dependency management is handled via uv and pyproject.toml to ensure consistent and traceable builds. Experiment tracking, logging, and result visualization will be handled using Weights and Biases (wandb), enabling comparison of models, hyperparameters, and detection performance across experiments.

The project will use publicly available fire and smoke video Fire-D dataset. The scope of the project is intentionally limited to allow iterative development over approximately six project days, starting with a minimal working pipeline and gradually adding complexity as time permits.
 


## Project structure

The directory structure of the project looks like this:
```txt
├── .github/                  # Github actions and dependabot
│   ├── dependabot.yaml
│   └── workflows/
│       └── tests.yaml
├── configs/                  # Configuration files
├── data/                     # Data directory
│   ├── processed
│   └── raw
├── dockerfiles/              # Dockerfiles
│   ├── api.Dockerfile
│   └── train.Dockerfile
├── docs/                     # Documentation
│   ├── mkdocs.yml
│   └── source/
│       └── index.md
├── models/                   # Trained models
├── notebooks/                # Jupyter notebooks
├── reports/                  # Reports
│   └── figures/
├── src/                      # Source code
│   ├── project_name/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── data.py
│   │   ├── evaluate.py
│   │   ├── models.py
│   │   ├── train.py
│   │   └── visualize.py
└── tests/                    # Tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_data.py
│   └── test_model.py
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── pyproject.toml            # Python project file
├── README.md                 # Project README
├── requirements.txt          # Project requirements
├── requirements_dev.txt      # Development requirements
└── tasks.py                  # Project tasks
```


Created using [mlops_template](https://github.com/SkafteNicki/mlops_template),
a [cookiecutter template](https://github.com/cookiecutter/cookiecutter) for getting
started with Machine Learning Operations (MLOps).
