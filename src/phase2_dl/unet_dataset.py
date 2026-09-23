import os
import numpy as np
import rasterio
import torch
from torch.utils.data import Dataset


IMAGE_DIR = "data/satellite/chips"
LABEL_DIR = "data/satellite/label_chips"

YEARS = [2020, 2025]

NUM_CLASSES = 5
IGNORE_LABEL = 255


class GeoSenseDataset(Dataset):

    def __init__(self, samples):
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):

        image_path, label_path = self.samples[index]

        # ---------------------------------------
        # Read 6-band Sentinel-2 image chip
        # ---------------------------------------
        with rasterio.open(image_path) as src:
            image = src.read().astype(np.float32)

        # Expected:
        # (6, 224, 224)

        # ---------------------------------------
        # Read label chip
        # ---------------------------------------
        label = np.load(label_path).astype(np.int64)

        # ---------------------------------------
        # Replace invalid NaN/Inf values
        # ---------------------------------------
        image = np.nan_to_num(
            image,
            nan=0.0,
            posinf=0.0,
            neginf=0.0
        )

        # ---------------------------------------
        # Convert to PyTorch tensors
        # ---------------------------------------
        image = torch.from_numpy(image)
        label = torch.from_numpy(label)

        return image, label


def create_samples():

    samples = []

    for year in YEARS:

        image_dir = os.path.join(
            IMAGE_DIR,
            str(year)
        )

        label_dir = os.path.join(
            LABEL_DIR,
            str(year)
        )

        for i in range(1, 92):

            image_file = os.path.join(
                image_dir,
                f"chip_{i:05d}.tif"
            )

            label_file = os.path.join(
                label_dir,
                f"label_{i:05d}.npy"
            )

            if os.path.exists(image_file) and os.path.exists(label_file):

                samples.append(
                    (image_file, label_file)
                )

            else:

                print(
                    f"WARNING: Missing pair for {year}, chip {i:05d}"
                )

    return samples


if __name__ == "__main__":

    print("=" * 60)
    print("GeoSense Agent 2.0")
    print("Exercise 3 - U-Net Dataset Test")
    print("=" * 60)

    samples = create_samples()

    print(f"\nTotal image-label pairs: {len(samples)}")

    dataset = GeoSenseDataset(samples)

    print(f"Dataset length: {len(dataset)}")

    # Test first sample
    image, label = dataset[0]

    print("\nFirst sample:")
    print(f"Image shape: {image.shape}")
    print(f"Image dtype: {image.dtype}")

    print(f"Label shape: {label.shape}")
    print(f"Label dtype: {label.dtype}")

    print("\nUnique label values:")
    print(torch.unique(label))

    # Check image values
    print("\nImage statistics:")
    print(f"Minimum: {image.min().item():.4f}")
    print(f"Maximum: {image.max().item():.4f}")
    print(f"Mean:    {image.mean().item():.4f}")

    print("\n" + "=" * 60)
    print("Dataset test completed.")
    print("=" * 60)