from torch.utils.data import Dataset

from forestfires_project.data import FireDataset


def test_fire_dataset():
    """Test the FireDataset class."""
    dataset = FireDataset(
        img_dir="data/samples/images",
        label_dir="data/samples/labels",
        classes={0: "fire", 1: "smoke"},
    )
    assert isinstance(dataset, Dataset)
