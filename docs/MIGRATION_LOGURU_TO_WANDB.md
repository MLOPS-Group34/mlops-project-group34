# Migration from Loguru to Weights & Biases

## Summary

This document describes the changes made to migrate from loguru logging to Weights & Biases (wandb) for experiment tracking and logging.

## Changes Made

### 1. Dependencies Updated

**File: `pyproject.toml`**
- Removed: `loguru>=0.7.3`
- Added: `python-dotenv>=1.0.0` (for loading environment variables)
- Kept: `wandb>=0.24.0` (already present)

### 2. Source Code Changes

#### `src/forestfires_project/train.py`
- Removed `from loguru import logger`
- Added `import wandb` and `from dotenv import load_dotenv`
- Replaced loguru logging setup with wandb initialization:
  ```python
  wandb.init(
      project=config['wandb_project'],
      name=config['project_name'],
      config=config
  )
  ```
- Replaced `logger.info()` calls with `print()` statements
- Added `wandb.finish()` at the end of training

#### `src/forestfires_project/model.py`
- Removed `from loguru import logger`
- Added `import wandb`
- Replaced logger calls with print statements
- Added automatic metrics logging (YOLO's built-in wandb integration)
- Added explicit final metrics logging:
  ```python
  final_metrics = {
      'final/mAP50': results.results_dict.get('metrics/mAP50(B)', 0),
      'final/mAP50-95': results.results_dict.get('metrics/mAP50-95(B)', 0),
      'final/precision': results.results_dict.get('metrics/precision(B)', 0),
      'final/recall': results.results_dict.get('metrics/recall(B)', 0),
  }
  wandb.log(final_metrics)
  ```

#### `src/forestfires_project/evaluate.py`
- Removed `from loguru import logger`
- Added `import wandb` and `from dotenv import load_dotenv`
- Added `use_wandb` parameter (default: True) to allow disabling wandb logging
- Initialized wandb for evaluation runs with job_type="evaluation"
- Added evaluation metrics logging:
  ```python
  eval_metrics = {
      'eval/mAP50': map50,
      'eval/mAP50-95': map5095,
      'eval/precision': p,
      'eval/recall': r
  }
  wandb.log(eval_metrics)
  ```
- Replaced logger calls with print statements

#### `src/forestfires_project/data.py`
- Removed `from loguru import logger`
- Replaced all `logger.info()` and `logger.warning()` calls with `print()` statements

#### `src/forestfires_project/visualize.py`
- Removed `from loguru import logger`
- Replaced logger calls with print statements

#### `main.py`
- Removed `from loguru import logger`
- Removed log file setup
- Replaced logger calls with print statements

### 3. Configuration Files

#### `.env.example` (NEW)
Created example environment file with:
```
WANDB_API_KEY=your_wandb_api_key_here
# WANDB_MODE=offline
```

#### `configs/config.yaml`
Already contained wandb configuration (no changes needed):
```yaml
wandb_project: "mlops_project_group34"
project_name: "forest_fire_detection"
```

### 4. Documentation

#### `docs/WANDB_INTEGRATION.md` (NEW)
Created comprehensive documentation covering:
- Setup instructions
- Configuration details
- Logged metrics explanation
- Usage examples
- Troubleshooting guide

## Metrics Tracked by Wandb

### Automatic Metrics (via Ultralytics YOLO)
During training, YOLO automatically logs:
- Training losses (box_loss, cls_loss, dfl_loss)
- Validation metrics per epoch (precision, recall, mAP50, mAP50-95)
- Learning rate
- Sample images with predictions

### Custom Metrics
We explicitly log:
- Final training metrics (mAP50, mAP50-95, precision, recall)
- Evaluation metrics on test set

## Benefits of Wandb over Loguru

1. **Experiment Tracking**: All experiments are tracked in one place with full version control
2. **Metric Visualization**: Real-time graphs and charts of training metrics
3. **Comparison**: Easy comparison of multiple runs side-by-side
4. **Model Checkpointing**: Automatic model artifact tracking
5. **Collaboration**: Share results with team members via web dashboard
6. **Reproducibility**: Full configuration and hyperparameter logging
7. **System Monitoring**: Automatic logging of GPU, CPU, memory usage

## Migration Checklist

- [x] Removed loguru from dependencies
- [x] Added python-dotenv to dependencies
- [x] Replaced loguru imports with wandb
- [x] Updated train.py with wandb initialization
- [x] Updated model.py with metrics logging
- [x] Updated evaluate.py with wandb logging
- [x] Updated data.py, visualize.py, and main.py
- [x] Created .env.example file
- [x] Created WANDB_INTEGRATION.md documentation
- [x] Verified no loguru references remain

## Next Steps

1. Copy `.env.example` to `.env` and add your wandb API key
2. Run `uv sync` to update dependencies
3. Test training with: `uv run python main.py --pipeline train`
4. View results at: https://wandb.ai/<your-username>/mlops_project_group34
