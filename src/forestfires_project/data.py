import os
import cv2
import yaml
import glob
import random
from pathlib import Path
from loguru import logger
from torch.utils.data import Dataset, DataLoader

class FireDataset(Dataset):
    """Custom Dataset for loading images and labels for Visualization/Manual Eval"""
    def __init__(self, img_dir, label_dir, classes, file_list=None):
        """
        Args:
            img_dir: Directory containing images
            label_dir: Directory containing label files
            classes: Dictionary of class mappings
            file_list: Optional list of filenames (without extension) to use
        """
        if file_list is not None:
            # Use specific file list
            self.img_files = sorted([os.path.join(img_dir, f"{fname}.jpg") for fname in file_list])
        else:
            # Use all images in directory
            self.img_files = sorted(glob.glob(os.path.join(img_dir, "*.jpg")))
        
        self.label_dir = label_dir
        self.classes = classes

    def __len__(self):
        return len(self.img_files)

    def __getitem__(self, idx):
        img_path = self.img_files[idx]
        file_name = os.path.basename(img_path).replace('.jpg', '.txt')
        label_path = os.path.join(self.label_dir, file_name)

        # Load Image
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, _ = img.shape

        boxes = []
        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    # YOLO format: class x_center y_center width height
                    parts = list(map(float, line.strip().split()))
                    cls = int(parts[0])
                    # Convert to absolute coordinates for visualization
                    x_c, y_c, bw, bh = parts[1], parts[2], parts[3], parts[4]
                    x1 = int((x_c - bw / 2) * w)
                    y1 = int((y_c - bh / 2) * h)
                    x2 = int((x_c + bw / 2) * w)
                    y2 = int((y_c + bh / 2) * h)
                    boxes.append([x1, y1, x2, y2, cls])

        return img, boxes, img_path

def sample_dataset(img_dir, label_dir, num_samples, random_seed=42):
    """
    Randomly sample a subset of images from a dataset directory.
    Returns list of sampled image filenames (without extension).
    """
    # Get all image files
    all_images = glob.glob(os.path.join(img_dir, "*.jpg"))
    
    if not all_images:
        logger.warning(f"No images found in {img_dir}")
        return []
    
    # Sample if needed
    if num_samples is not None and num_samples < len(all_images):
        random.seed(random_seed)
        sampled_images = random.sample(all_images, num_samples)
        logger.info(f"Sampled {num_samples} images from {len(all_images)} available in {os.path.basename(img_dir)}")
    else:
        sampled_images = all_images
        logger.info(f"Using all {len(all_images)} images from {os.path.basename(img_dir)}")
    
    # Return just the filenames without path and extension
    return [os.path.splitext(os.path.basename(img))[0] for img in sampled_images]

def create_yolo_yaml(config, config_path):
    """Generates the data.yaml file required by Ultralytics YOLO with optional sampling"""
    # Resolve root from config file location
    config_dir = os.path.dirname(config_path)
    root = os.path.abspath(os.path.join(config_dir, config['paths']['root_dir']))
    
    # Convert classes dict to list in correct order (YOLO expects a list)
    classes_dict = config['hyperparameters']['classes']
    class_names = [classes_dict[i] for i in sorted(classes_dict.keys())]
    
    # Check if sampling is enabled
    sampling_config = config.get('data_sampling', {})
    sampling_enabled = sampling_config.get('enabled', False)
    
    if sampling_enabled:
        logger.info("Data sampling is ENABLED")
        random_seed = sampling_config.get('random_seed', 42)
        
        # Sample train data
        train_img_dir = os.path.join(root, config['paths']['train_images'])
        train_lbl_dir = os.path.join(root, config['paths']['train_labels'])
        train_samples = sampling_config.get('train_samples')
        train_files = sample_dataset(train_img_dir, train_lbl_dir, train_samples, random_seed)
        
        # Sample val data
        val_img_dir = os.path.join(root, config['paths']['val_images'])
        val_lbl_dir = os.path.join(root, config['paths']['val_labels'])
        val_samples = sampling_config.get('val_samples')
        val_files = sample_dataset(val_img_dir, val_lbl_dir, val_samples, random_seed)
        
        # Sample test data
        test_img_dir = os.path.join(root, config['paths']['test_images'])
        test_lbl_dir = os.path.join(root, config['paths']['test_labels'])
        test_samples = sampling_config.get('test_samples')
        test_files = sample_dataset(test_img_dir, test_lbl_dir, test_samples, random_seed)
        
        # Create .txt files with absolute paths for YOLO
        train_txt = os.path.join(root, "train_sampled.txt")
        val_txt = os.path.join(root, "val_sampled.txt")
        test_txt = os.path.join(root, "test_sampled.txt")
        
        with open(train_txt, 'w') as f:
            for fname in train_files:
                f.write(os.path.join(train_img_dir, f"{fname}.jpg") + '\n')
        
        with open(val_txt, 'w') as f:
            for fname in val_files:
                f.write(os.path.join(val_img_dir, f"{fname}.jpg") + '\n')
        
        with open(test_txt, 'w') as f:
            for fname in test_files:
                f.write(os.path.join(test_img_dir, f"{fname}.jpg") + '\n')
        
        logger.info(f"Created sample lists: {train_txt}, {val_txt}, {test_txt}")
        
        # YOLO expects paths relative to 'path' or absolute paths in .txt files
        data_yaml = {
            'path': root,
            'train': os.path.basename(train_txt),
            'val': os.path.basename(val_txt),
            'test': os.path.basename(test_txt),
            'nc': len(class_names),
            'names': class_names  # List in correct order
        }
    else:
        logger.info("Data sampling is DISABLED - using all available data")
        # Original behavior - use directory paths
        data_yaml = {
            'path': root,
            'train': config['paths']['train_images'],
            'val': config['paths']['val_images'],
            'test': config['paths']['test_images'],
            'nc': len(class_names),
            'names': class_names  # List in correct order
        }
    
    yaml_path = os.path.join(root, config['paths']['yolo_yaml'])
    
    with open(yaml_path, 'w') as f:
        yaml.dump(data_yaml, f, default_flow_style=False)
    
    logger.info(f"YOLO data configuration saved to {yaml_path}")
    return yaml_path

def get_test_loader(config, config_path):
    """Returns a PyTorch DataLoader for the test set with optional sampling"""
    # Resolve root from config file location
    config_dir = os.path.dirname(config_path)
    root = os.path.abspath(os.path.join(config_dir, config['paths']['root_dir']))
    img_dir = os.path.join(root, config['paths']['test_images'])
    lbl_dir = os.path.join(root, config['paths']['test_labels'])
    
    # Check if sampling is enabled
    sampling_config = config.get('data_sampling', {})
    sampling_enabled = sampling_config.get('enabled', False)
    file_list = None
    
    if sampling_enabled:
        random_seed = sampling_config.get('random_seed', 42)
        test_samples = sampling_config.get('test_samples')
        file_list = sample_dataset(img_dir, lbl_dir, test_samples, random_seed)
    
    dataset = FireDataset(img_dir, lbl_dir, config['hyperparameters']['classes'], file_list=file_list)
    
    # Collate function needed because boxes have variable length
    def collate_fn(batch):
        return tuple(zip(*batch))

    return DataLoader(dataset, batch_size=6, shuffle=True, collate_fn=collate_fn)