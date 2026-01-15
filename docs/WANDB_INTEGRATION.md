# Weights & Biases Integration

This project uses **Weights & Biases (wandb)** for experiment tracking and logging of training metrics.

## Setup

1. **Create a wandb account**: Go to [https://wandb.ai/](https://wandb.ai/) and sign up for a free account.

2. **Get your API key**: After signing in, go to [https://wandb.ai/authorize](https://wandb.ai/authorize) to get your API key.

3. **Create a .env file**: Copy the example file and add your API key:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your API key:
   ```
   WANDB_API_KEY=your_actual_api_key_here
   ```

4. **Install dependencies**: Make sure python-dotenv and wandb are installed (already included in pyproject.toml):
   ```bash
   uv sync
   ```

## Configuration

The wandb project name is configured in `configs/config.yaml`:

```yaml
project_name: "forest_fire_detection"
wandb_project: "mlops_project_group34"
```

- `wandb_project`: The name of your wandb project (where all experiments will be logged)
- `project_name`: The name of the specific run/experiment

## Logged Metrics

### During Training (automatic via Ultralytics YOLO integration)

The Ultralytics YOLO library has **built-in wandb integration**. When wandb is initialized, YOLO automatically logs:

- **Training losses**:
  - `train/box_loss`: Bounding box regression loss
  - `train/cls_loss`: Classification loss
  - `train/dfl_loss`: Distribution focal loss
  
- **Validation metrics** (per epoch):
  - `metrics/precision(B)`: Precision for bounding boxes
  - `metrics/recall(B)`: Recall for bounding boxes
  - `metrics/mAP50(B)`: Mean Average Precision at IoU threshold 0.5
  - `metrics/mAP50-95(B)`: Mean Average Precision averaged over IoU thresholds 0.5-0.95

- **Learning rate**: Current learning rate at each step
- **Images**: Sample training/validation images with predictions

### Final Training Metrics

After training completes, the following final metrics are logged:

- `final/mAP50`: Final mAP at IoU 0.5
- `final/mAP50-95`: Final mAP averaged over IoU 0.5-0.95
- `final/precision`: Final precision
- `final/recall`: Final recall

### Evaluation Metrics

When running evaluation, the following metrics are logged:

- `eval/mAP50`: Test set mAP at IoU 0.5
- `eval/mAP50-95`: Test set mAP averaged over IoU 0.5-0.95
- `eval/precision`: Test set precision
- `eval/recall`: Test set recall

## Usage

### Training with wandb

```bash
# Make sure your .env file contains WANDB_API_KEY
uv run python main.py --pipeline train --config configs/config.yaml
```

Or run training directly:
```bash
uv run python -c "from src.forestfires_project.train import run_training; run_training()"
```

### Evaluation with wandb

```bash
uv run python main.py --pipeline evaluate --config configs/config.yaml
```

To run evaluation **without** wandb logging:
```python
from src.forestfires_project.evaluate import run_evaluation
run_evaluation(use_wandb=False)
```

## Viewing Results

After training/evaluation, you can view your results at:
```
https://wandb.ai/<your-username>/mlops_project_group34
```

You'll be able to see:
- Real-time training metrics and losses
- Validation metrics per epoch
- Learning rate schedules
- Sample predictions on training/validation images
- Model configuration and hyperparameters
- System metrics (GPU usage, memory, etc.)

## Offline Mode

If you want to run wandb in offline mode (useful for debugging or when internet is unavailable), add to your `.env`:

```
WANDB_MODE=offline
```

Later, you can sync the offline runs with:
```bash
wandb sync wandb/offline-run-*
```

## Troubleshooting

### API Key Issues

If you see authentication errors:
1. Make sure `.env` file exists in the project root
2. Check that `WANDB_API_KEY` is set correctly (no quotes or extra spaces)
3. Try running `uv run wandb login` manually

### Missing Metrics

If some metrics are not showing up:
1. Make sure wandb is initialized before training starts
2. Check that the Ultralytics version is >= 8.3.251
3. Verify that the training is actually running (not failing silently)

### Multiple Runs

Each time you run training, a new wandb run is created. You can:
- Compare multiple runs in the wandb dashboard
- Group runs by tags or names
- Create custom visualizations in wandb
