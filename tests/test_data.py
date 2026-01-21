import logging
from torch.utils.data import Dataset
from forestfires_project.data import FireDataset

img_path = "data/samples/test/images"
label_path = "data/samples/test/labels"

logging.basicConfig(level=logging.INFO)


def test_fire_dataset():
    """
    Test that FireDataset initializes and returns a torch Dataset instance.
    """
    dataset = FireDataset(
        img_dir=img_path,
        label_dir=label_path,
        classes={0: "fire", 1: "smoke"},
    )
    logging.info(f"Initialized FireDataset with {len(dataset)} samples.")
    assert isinstance(dataset, Dataset)


def test_dataset_length():
    """
    Test that the dataset contains at least the minimum expected number of samples.
    """
    dataset = FireDataset(
        img_dir=img_path,
        label_dir=label_path,
        classes={0: "fire", 1: "smoke"},
    )
    logging.info(f"Dataset length: {len(dataset)}")
    min_expected_length = 10  # Change as needed
    assert len(dataset) >= min_expected_length, f"Dataset too small: {len(dataset)}"


def test_image_shape():
    """
    Test that the first image in the dataset has the expected shape (height, width, channels).
    """
    dataset = FireDataset(
        img_dir=img_path,
        label_dir=label_path,
        classes={0: "fire", 1: "smoke"},
    )
    expected_shape = (640, 640, 3)
    img, label, image_file_path = dataset[0]
    logging.info(f"First image path: {image_file_path}")
    logging.info(f"First image shape: {getattr(img, 'shape', None)}")
    assert hasattr(img, "shape"), "Image does not have shape attribute"
    assert tuple(img.shape) == expected_shape, f"Image shape {img.shape} != {expected_shape}"


def test_label_validity():
    """
    Test that all label class indices in the first sample are valid (in {0, 1}).
    """

    dataset = FireDataset(
        img_dir=img_path,
        label_dir=label_path,
        classes={0: "fire", 1: "smoke"},
    )
    valid_labels = {0, 1}
    img, label, image_file_path = dataset[0]
    logging.info(f"First label: {label}")
    logging.info(f"First image path: {image_file_path}")
    # If label is a list of lists, check each label's class index
    if isinstance(label, list) and all(isinstance(i, list) for i in label):
        for i in label:
            class_idx = i[-1]
            logging.info(f"Checking class index: {class_idx}")
            assert class_idx in valid_labels, f"Label class {class_idx} not in {valid_labels}"
    else:
        if hasattr(label, "item"):
            label = label.item()
        logging.info(f"Checking class index: {label}")
        assert label in valid_labels, f"Label {label} not in {valid_labels}"
