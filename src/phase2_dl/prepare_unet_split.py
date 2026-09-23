import os
import random
import numpy as np
from collections import Counter


IMAGE_DIR = "data/satellite/chips"
LABEL_DIR = "data/satellite/label_chips"

YEARS = [2020, 2025]

NUM_CLASSES = 5
IGNORE_LABEL = 255

TRAIN_RATIO = 0.80
SEED = 42


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
                    (year, i, image_file, label_file)
                )

    return samples


def calculate_class_counts(samples):

    counts = np.zeros(NUM_CLASSES, dtype=np.int64)

    for year, chip_id, image_file, label_file in samples:

        label = np.load(label_file)

        for class_id in range(NUM_CLASSES):

            counts[class_id] += np.sum(
                label == class_id
            )

    return counts


def calculate_class_weights(counts):

    total = counts.sum()

    weights = total / (
        NUM_CLASSES * counts
    )

    return weights


if __name__ == "__main__":

    print("=" * 60)
    print("GeoSense Agent 2.0")
    print("Exercise 3 - Train / Validation Split")
    print("=" * 60)

    # ---------------------------------------
    # Create samples
    # ---------------------------------------

    samples = create_samples()

    print(f"\nTotal samples: {len(samples)}")

    # ---------------------------------------
    # Shuffle reproducibly
    # ---------------------------------------

    random.seed(SEED)

    random.shuffle(samples)

    # ---------------------------------------
    # 80/20 split
    # ---------------------------------------

    split_index = int(
        len(samples) * TRAIN_RATIO
    )

    train_samples = samples[:split_index]
    val_samples = samples[split_index:]

    print(f"Training samples:   {len(train_samples)}")
    print(f"Validation samples: {len(val_samples)}")

    # ---------------------------------------
    # Year distribution
    # ---------------------------------------

    train_years = Counter(
        sample[0] for sample in train_samples
    )

    val_years = Counter(
        sample[0] for sample in val_samples
    )

    print("\nTraining year distribution:")
    print(train_years)

    print("\nValidation year distribution:")
    print(val_years)

    # ---------------------------------------
    # Class counts
    # ---------------------------------------

    print("\nCalculating class distribution...")

    class_counts = calculate_class_counts(
        train_samples
    )

    print("\nTraining pixel counts:")

    class_names = [
        "Urban",
        "Vegetation",
        "Water",
        "Bare Land",
        "Agriculture"
    ]

    for i in range(NUM_CLASSES):

        print(
            f"{class_names[i]:12s}: "
            f"{class_counts[i]:,}"
        )

    # ---------------------------------------
    # Class weights
    # ---------------------------------------

    weights = calculate_class_weights(
        class_counts
    )

    print("\nClass weights:")

    for i in range(NUM_CLASSES):

        print(
            f"{class_names[i]:12s}: "
            f"{weights[i]:.6f}"
        )

    # ---------------------------------------
    # Save split
    # ---------------------------------------

    os.makedirs(
        "data/satellite/splits",
        exist_ok=True
    )

    np.save(
        "data/satellite/splits/train_samples.npy",
        np.array(train_samples, dtype=object)
    )

    np.save(
        "data/satellite/splits/val_samples.npy",
        np.array(val_samples, dtype=object)
    )

    np.save(
        "data/satellite/splits/class_weights.npy",
        weights
    )

    print("\nSaved files:")

    print(
        "data/satellite/splits/train_samples.npy"
    )

    print(
        "data/satellite/splits/val_samples.npy"
    )

    print(
        "data/satellite/splits/class_weights.npy"
    )

    print("\n" + "=" * 60)
    print("Train / validation preparation completed.")
    print("=" * 60)