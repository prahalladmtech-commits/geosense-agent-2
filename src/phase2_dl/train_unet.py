import os
import json
import numpy as np
import rasterio

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

import segmentation_models_pytorch as smp

import albumentations as A


# ============================================================
# Configuration
# ============================================================

TRAIN_FILE = "data/satellite/splits/train_samples.npy"
VAL_FILE = "data/satellite/splits/val_samples.npy"
WEIGHTS_FILE = "data/satellite/splits/class_weights.npy"

MODEL_DIR = "models/saved"
OUTPUT_DIR = "outputs/reports"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


NUM_CLASSES = 5
IN_CHANNELS = 6

BATCH_SIZE = 8
NUM_EPOCHS = 30

LEARNING_RATE = 0.001

SEED = 42


CLASS_NAMES = [
    "Urban",
    "Vegetation",
    "Water",
    "Bare Land",
    "Agriculture"
]


# ============================================================
# Reproducibility
# ============================================================

torch.manual_seed(SEED)
np.random.seed(SEED)


# ============================================================
# Dataset
# ============================================================

class GeoSenseDataset(Dataset):

    def __init__(self, samples, augment=False):

        self.samples = samples
        self.augment = augment

        if augment:

            self.transform = A.Compose([
                A.HorizontalFlip(p=0.5),
                A.VerticalFlip(p=0.5),
                A.RandomRotate90(p=0.5)
            ])

        else:

            self.transform = None


    def __len__(self):

        return len(self.samples)


    def __getitem__(self, index):

        year, chip_id, image_path, label_path = self.samples[index]

        # ---------------------------------------
        # Read image
        # ---------------------------------------

        with rasterio.open(image_path) as src:

            image = src.read().astype(np.float32)

        # ---------------------------------------
        # Read label
        # ---------------------------------------

        label = np.load(label_path).astype(np.int64)

        # ---------------------------------------
        # Remove invalid values
        # ---------------------------------------

        image = np.nan_to_num(
            image,
            nan=0.0,
            posinf=0.0,
            neginf=0.0
        )

        # ---------------------------------------
        # Convert:
        #
        # (C,H,W) -> (H,W,C)
        # ---------------------------------------

        image = np.transpose(
            image,
            (1, 2, 0)
        )

        # ---------------------------------------
        # Augmentation
        # ---------------------------------------

        if self.transform is not None:

            transformed = self.transform(
                image=image,
                mask=label
            )

            image = transformed["image"]
            label = transformed["mask"]

        # ---------------------------------------
        # Convert back:
        #
        # (H,W,C) -> (C,H,W)
        # ---------------------------------------

        image = np.transpose(
            image,
            (2, 0, 1)
        )

        # ---------------------------------------
        # Torch tensors
        # ---------------------------------------

        image = torch.from_numpy(
            image.copy()
        ).float()

        label = torch.from_numpy(
            label.copy()
        ).long()

        return image, label


# ============================================================
# Load samples
# ============================================================

train_samples = np.load(
    TRAIN_FILE,
    allow_pickle=True
)

val_samples = np.load(
    VAL_FILE,
    allow_pickle=True
)


print("=" * 60)
print("GeoSense Agent 2.0")
print("Exercise 3 - U-Net Training")
print("=" * 60)

print(f"\nTraining samples:   {len(train_samples)}")
print(f"Validation samples: {len(val_samples)}")


# ============================================================
# Dataset and DataLoader
# ============================================================

train_dataset = GeoSenseDataset(
    train_samples,
    augment=True
)

val_dataset = GeoSenseDataset(
    val_samples,
    augment=False
)


train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0,
    pin_memory=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=True
)


print(f"\nTraining batches:   {len(train_loader)}")
print(f"Validation batches: {len(val_loader)}")


# ============================================================
# Device
# ============================================================

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"\nDevice: {device}")

if torch.cuda.is_available():

    print(
        f"GPU: {torch.cuda.get_device_name(0)}"
    )


# ============================================================
# U-Net model
# ============================================================

model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights=None,
    in_channels=IN_CHANNELS,
    classes=NUM_CLASSES
)

model = model.to(device)


print("\nModel:")
print("U-Net")
print("Encoder: ResNet34")
print("Input channels: 6")
print("Output classes: 5")


# ============================================================
# Class weights
# ============================================================

raw_weights = np.load(
    WEIGHTS_FILE
)

print("\nOriginal class weights:")

for name, weight in zip(
    CLASS_NAMES,
    raw_weights
):

    print(
        f"{name:12s}: {weight:.6f}"
    )


# ------------------------------------------------------------
# Smooth the extreme Urban weight
# ------------------------------------------------------------

weights = np.sqrt(raw_weights)

weights = weights / weights.mean()

class_weights = torch.tensor(
    weights,
    dtype=torch.float32,
    device=device
)


print("\nSmoothed class weights:")

for name, weight in zip(
    CLASS_NAMES,
    weights
):

    print(
        f"{name:12s}: {weight:.6f}"
    )


# ============================================================
# Loss
# ============================================================

criterion = nn.CrossEntropyLoss(
    weight=class_weights,
    ignore_index=255
)


# ============================================================
# Optimizer
# ============================================================

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)


# ============================================================
# Learning rate scheduler
# ============================================================

scheduler = torch.optim.lr_scheduler.StepLR(
    optimizer,
    step_size=10,
    gamma=0.5
)


# ============================================================
# Training history
# ============================================================

history = {

    "train_loss": [],
    "val_loss": [],
    "train_accuracy": [],
    "val_accuracy": [],
    "learning_rate": []

}


best_val_loss = float("inf")


# ============================================================
# Training loop
# ============================================================

for epoch in range(NUM_EPOCHS):

    print(
        f"\nEpoch {epoch + 1}/{NUM_EPOCHS}"
    )

    print("-" * 60)


    # ========================================================
    # TRAIN
    # ========================================================

    model.train()

    running_loss = 0.0

    correct = 0
    total = 0


    for images, labels in train_loader:

        images = images.to(
            device,
            non_blocking=True
        )

        labels = labels.to(
            device,
            non_blocking=True
        )


        optimizer.zero_grad()


        outputs = model(images)


        loss = criterion(
            outputs,
            labels
        )


        loss.backward()

        optimizer.step()


        running_loss += (
            loss.item() *
            images.size(0)
        )


        predictions = torch.argmax(
            outputs,
            dim=1
        )


        valid = labels != 255


        correct += (
            (predictions[valid] ==
             labels[valid]).sum().item()
        )

        total += valid.sum().item()


    train_loss = (
        running_loss /
        len(train_loader.dataset)
    )


    train_accuracy = (
        correct / total
        if total > 0
        else 0
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    model.eval()

    val_loss_total = 0.0

    val_correct = 0
    val_total = 0


    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(
                device,
                non_blocking=True
            )

            labels = labels.to(
                device,
                non_blocking=True
            )


            outputs = model(images)


            loss = criterion(
                outputs,
                labels
            )


            val_loss_total += (
                loss.item() *
                images.size(0)
            )


            predictions = torch.argmax(
                outputs,
                dim=1
            )


            valid = labels != 255


            val_correct += (
                (predictions[valid] ==
                 labels[valid]).sum().item()
            )

            val_total += valid.sum().item()


    val_loss = (
        val_loss_total /
        len(val_loader.dataset)
    )


    val_accuracy = (
        val_correct / val_total
        if val_total > 0
        else 0
    )


    # ========================================================
    # Scheduler
    # ========================================================

    scheduler.step()


    current_lr = optimizer.param_groups[0]["lr"]


    # ========================================================
    # Save history
    # ========================================================

    history["train_loss"].append(
        train_loss
    )

    history["val_loss"].append(
        val_loss
    )

    history["train_accuracy"].append(
        train_accuracy
    )

    history["val_accuracy"].append(
        val_accuracy
    )

    history["learning_rate"].append(
        current_lr
    )


    # ========================================================
    # Print results
    # ========================================================

    print(
        f"Train Loss: {train_loss:.4f}"
    )

    print(
        f"Val Loss:   {val_loss:.4f}"
    )

    print(
        f"Train Acc:  {train_accuracy * 100:.2f}%"
    )

    print(
        f"Val Acc:    {val_accuracy * 100:.2f}%"
    )

    print(
        f"Learning Rate: {current_lr:.6f}"
    )


    # ========================================================
    # Save best model
    # ========================================================

    if val_loss < best_val_loss:

        best_val_loss = val_loss

        torch.save(
            model.state_dict(),
            os.path.join(
                MODEL_DIR,
                "unet_best.pth"
            )
        )

        print(
            "✓ Best model saved."
        )


# ============================================================
# Save final model
# ============================================================

torch.save(
    model.state_dict(),
    os.path.join(
        MODEL_DIR,
        "unet_final.pth"
    )
)


# ============================================================
# Save history
# ============================================================

with open(
    os.path.join(
        MODEL_DIR,
        "unet_history.json"
    ),
    "w"
) as f:

    json.dump(
        history,
        f,
        indent=4
    )


print("\n" + "=" * 60)
print("U-Net training completed.")
print("=" * 60)

print(
    f"\nBest validation loss: "
    f"{best_val_loss:.4f}"
)

print("\nSaved models:")

print(
    "models/saved/unet_best.pth"
)

print(
    "models/saved/unet_final.pth"
)

print(
    "models/saved/unet_history.json"
)

print("\n" + "=" * 60)