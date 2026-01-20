# Creating Custom Wandb Dashboards

## What You'll See in Wandb

When you run training with the updated configuration, wandb will automatically create a dashboard with:

### 1. **Overview Tab**
- Quick summary of all metrics
- Training duration and status
- Number of epochs completed

### 2. **Charts Tab**
Shows continuous graphs for all logged metrics:

#### Training Curves
```
train/box_loss      → Line graph showing box loss decreasing over epochs
train/cls_loss      → Line graph showing classification loss over epochs
train/dfl_loss      → Distribution focal loss over epochs
```

#### Validation Metrics
```
metrics/precision(B)    → Precision improving over epochs
metrics/recall(B)       → Recall improving over epochs
metrics/mAP50(B)        → mAP@0.5 improving over epochs
metrics/mAP50-95(B)     → mAP@0.5-0.95 improving over epochs
```

#### Learning Rate
```
lr                      → Learning rate schedule during training
```

#### Final Metrics
```
final/mAP50, final/precision, final/recall, final/box_loss, final/cls_loss
```

### 3. **System Tab**
- **Now Disabled** - System metrics are no longer logged to reduce clutter

## Customizing Your Dashboard

### Option 1: Add More Metrics During Training

Edit `src/forestfires_project/model.py` and modify the `final_metrics` dictionary:

```python
final_metrics = {
    'final/mAP50': results_dict.get('metrics/mAP50(B)', 0),
    'final/mAP50-95': results_dict.get('metrics/mAP50-95(B)', 0),
    'final/precision': results_dict.get('metrics/precision(B)', 0),
    'final/recall': results_dict.get('metrics/recall(B)', 0),
    'final/box_loss': results_dict.get('train/box_loss', 0),
    'final/cls_loss': results_dict.get('train/cls_loss', 0),
    # Add custom metrics here:
    'final/custom_metric': some_value,
}
```

### Option 2: Log Additional Metrics at Any Time

In your code, use:

```python
import wandb

# Log a single value
wandb.log({'custom_metric': 0.95})

# Log multiple values
wandb.log({
    'accuracy': 0.95,
    'f1_score': 0.92,
    'precision': 0.97
})

# Log a dictionary
metrics = {'loss': 0.05, 'accuracy': 0.95}
wandb.log(metrics)
```

### Option 3: Create a Custom Report in Wandb Web UI

1. Go to your wandb project dashboard
2. Click "Reports" in the left sidebar
3. Click "Create Report"
4. Drag and drop charts to create your custom layout
5. Add notes, images, and conclusions
6. Share with team members

### Option 4: Re-enable System Metrics

If you want to see GPU/CPU/Memory usage (useful for debugging):

Edit `src/forestfires_project/train.py`:

```python
# Change from:
settings=wandb.Settings(system_sample_rate=0)

# To:
settings=wandb.Settings(system_sample_rate=0.1)  # Logs every 10 seconds
```

Values: 0-1 (0 = disabled, 1 = every sample, 0.5 = every other sample)

## Comparing Multiple Runs

Wandb makes it easy to compare different training runs:

1. Run multiple training experiments:
   ```bash
   uv run python main.py --pipeline train --config configs/config.yaml
   ```

2. Each run gets a unique name automatically

3. In wandb dashboard:
   - Click "Runs" to see all your experiments
   - Select multiple runs to compare side-by-side
   - View which hyperparameters gave best results

## Example: Good Dashboard Setup

For a clean, focused dashboard monitoring training:

```
Row 1: Loss Curves
├── train/box_loss
├── train/cls_loss
└── train/dfl_loss

Row 2: Validation Metrics
├── metrics/precision(B)
├── metrics/recall(B)
├── metrics/mAP50(B)
└── metrics/mAP50-95(B)

Row 3: Learning Rate
└── lr

Row 4: Final Summary
├── final/mAP50
├── final/precision
├── final/recall
└── final/box_loss
```

This setup gives you complete visibility into:
- Whether loss is decreasing (good training)
- Whether metrics are improving (model learning)
- Learning rate schedule (optimizer behavior)
- Final performance summary

## Tips

✅ Use descriptive names for runs: `"v1_baseline"`, `"v2_larger_batch"`, etc.
✅ Compare runs to understand impact of hyperparameter changes
✅ Create reports to document experimental findings
✅ Use tags to group related runs: `tags=["baseline"]`, `tags=["experiment"]`
✅ Save best run URLs to share results with team
