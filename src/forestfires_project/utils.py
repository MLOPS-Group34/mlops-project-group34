"""
Utility functions for the Streamlit dashboard.
"""

from pathlib import Path


def get_prediction_grids(reports_dir: Path) -> list:
    """
    Get list of prediction grid PNG files from reports directory.
    
    Args:
        reports_dir: Path to reports/figures directory
    
    Returns:
        List of grid file paths sorted by grid number
    """
    grid_files = sorted([f for f in reports_dir.glob("predictions_grid_*.png")])
    return grid_files


def get_grid_info(grid_path: Path) -> dict:
    """
    Extract information about a grid file.
    
    Args:
        grid_path: Path to grid PNG file
    
    Returns:
        Dictionary with grid metadata
    """
    name = grid_path.stem  # e.g., "predictions_grid_1"
    grid_num = int(name.split("_")[-1])
    
    return {
        "path": grid_path,
        "name": name,
        "grid_num": grid_num,
        "size": grid_path.stat().st_size,
    }
