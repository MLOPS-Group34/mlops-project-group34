# Wandb Continuous Logging Configuration

## Changes Made

### Disabled System Metrics
- Updated `train.py` and `evaluate.py` to disable system metrics logging (GPU, memory, CPU usage)
- Added `settings=wandb.Settings(system_sample_rate=0)` to `wandb.init()` calls
- This reduces noise in wandb dashboards and focuses on ML metrics

### Enhanced Metric Logging
- Updated `model.py` to explicitly log losses and accuracies
- Now tracking both training and final metrics with better organization

## Metrics Being Logged

### During Training (Continuous Graphs)

YOLO automatically logs these metrics at each epoch:

**Training Metrics:**
- `train/box_loss` - Bounding box localization loss
- `train/cls_loss` - Classification loss
- `train/dfl_loss` - Distribution focal loss

**Validation Metrics (per epoch):**
- `metrics/precision(B)` - Precision on bounding boxes
- `metrics/recall(B)` - Recall on bounding boxes
- `metrics/mAP50(B)` - Mean Average Precision at IoU=0.5
- `metrics/mAP50-95(B)` - Mean Average Precision averaged over IoU 0.5-0.95

**Learning Rate:**
- `lr` - Current learning rate

### After Training Completes (Final Values)

- `final/mAP50` - Final mAP@0.5
- `final/mAP50-95` - Final mAP@0.5-0.95
- `final/precision` - Final precision
- `final/recall` - Final recall
- `final/box_loss` - Final box loss
- `final/cls_loss` - Final classification loss

### Evaluation Metrics

When running evaluation, these metrics are logged:

- `eval/mAP50` - Test set mAP@0.5
- `eval/mAP50-95` - Test set mAP@0.5-0.95
- `eval/precision` - Test set precision
- `eval/recall` - Test set recall

## Viewing the Graphs

When you visit your wandb dashboard at:
```
https://wandb.ai/<your-username>/mlops_project_group34
```

You'll see continuous graphs for:
1. **Training Loss** - Shows `train/box_loss`, `train/cls_loss`, `train/dfl_loss` over epochs
2. **Validation Metrics** - Shows `metrics/precision(B)`, `metrics/recall(B)`, `metrics/mAP50(B)`, `metrics/mAP50-95(B)` over epochs
3. **Learning Rate** - Shows how learning rate changes during training
4. **Final Metrics Summary** - Shows final values of all key metrics

## Benefits

✅ **Cleaner Dashboard** - No unnecessary system metrics
✅ **Focus on ML Metrics** - Only shows training/validation/evaluation metrics
✅ **Continuous Graphs** - Real-time visualization during training
✅ **Historical Comparison** - Compare multiple training runs side-by-side
✅ **Loss Tracking** - Monitor loss curves to detect overfitting

## Advanced Configuration

To customize what gets logged to wandb, you can modify:

1. **In `train.py`**: The `wandb.init()` settings
   - Change `system_sample_rate` to a value between 0-1 to enable partial system metrics
   - Add other wandb settings as needed

2. **In `model.py`**: The metrics logged after training
   - Modify the `final_metrics` dictionary to log additional metrics
   - Use `wandb.log()` to log custom metrics

Example: To enable system metrics again:
```python
wandb.init(
    ...,
    settings=wandb.Settings(system_sample_rate=0.5)  # Log system metrics every 2 seconds
)
```
