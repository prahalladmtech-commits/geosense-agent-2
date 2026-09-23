
import os
import re
import time
import numpy as np
import rasterio
import torch
import segmentation_models_pytorch as smp


BASE_DIR = "/content/GeoSense_Unet_Training_v2"
MODEL_DIR = "/content/drive/MyDrive/GeoSense/Phase2_models"

BEST_MODEL = os.path.join(MODEL_DIR, "unet_best.pth")
PRITHVI_MODEL = os.path.join(MODEL_DIR, "prithvi_finetuned.pth")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

NUM_CLASSES = 5
IN_CHANNELS = 6

CLASS_NAMES = [
    "Urban",
    "Vegetation",
    "Water",
    "Bare Land",
    "Agriculture"
]

CHANGE_THRESHOLD = 0.15


def resolve_path(saved_path):
    saved_path = str(saved_path)

    if saved_path.startswith("data/"):
        saved_path = saved_path[5:]

    if saved_path.startswith("satellite/"):
        saved_path = "satellite\\" + saved_path[len("satellite/"):]

    return os.path.join(BASE_DIR, saved_path)


def _load_model():
    """
    Load the fine-tuned Phase 2 model.

    Preferred:
        prithvi_finetuned.pth

    Fallback:
        unet_best.pth
    """

    if os.path.exists(PRITHVI_MODEL):
        print("Prithvi model found:")
        print(PRITHVI_MODEL)

        # Prithvi fine-tuned model loading can be added here
        # when the fine-tuned checkpoint is available.

    print("Prithvi model not found.")
    print("Falling back to U-Net:")
    print(BEST_MODEL)

    model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights=None,
        in_channels=IN_CHANNELS,
        classes=NUM_CLASSES
    )

    state_dict = torch.load(
        BEST_MODEL,
        map_location=DEVICE
    )

    model.load_state_dict(state_dict)

    model = model.to(DEVICE)
    model.eval()

    return model


def _find_chip_files(year):
    """
    Find chip files from the extracted dataset.

    The ZIP contains literal Windows backslashes inside
    the filenames, so the path is parsed from the filename.
    """

    chips = {}

    for root, dirs, files in os.walk(BASE_DIR):

        for filename in files:

            match = re.search(
                rf"^satellite\\chips\\{year}\\chip_(\d+)\.tif$",
                filename
            )

            if match is None:
                continue

            chip_id = int(match.group(1))
            full_path = os.path.join(root, filename)

            chips[chip_id] = full_path

    return chips


def _get_image_patch(lat, lon, radius_m):
    """
    Locate the 2025 chip containing the requested coordinate.

    Returns:
        patch: (6, 224, 224)
        chip_id: matched chip identifier
        image_path: source 2025 TIFF
    """

    chips_2025 = _find_chip_files(2025)

    for chip_id, image_path in chips_2025.items():

        with rasterio.open(image_path) as src:

            bounds = src.bounds

            if (
                bounds.left <= lon <= bounds.right
                and
                bounds.bottom <= lat <= bounds.top
            ):

                patch = src.read().astype(np.float32)

                patch = np.nan_to_num(
                    patch,
                    nan=0.0,
                    posinf=0.0,
                    neginf=0.0
                )

                if patch.shape[0] != IN_CHANNELS:
                    raise ValueError(
                        f"Expected {IN_CHANNELS} bands, "
                        f"found {patch.shape[0]}"
                    )

                if patch.shape[1:] != (224, 224):
                    raise ValueError(
                        f"Expected 224x224 patch, "
                        f"found {patch.shape[1:]}"
                    )

                # Fill zero pixels using band means.
                for band_idx in range(IN_CHANNELS):

                    band = patch[band_idx]

                    valid = band != 0

                    if np.any(valid):

                        band_mean = float(
                            band[valid].mean()
                        )

                        band[~valid] = band_mean

                return patch, chip_id, image_path

    raise ValueError(
        f"No 2025 chip contains coordinate "
        f"lat={lat}, lon={lon}"
    )


def _compute_ndvi_ndwi(patch):
    """
    Compute NDVI and NDWI.

    Band order:
        B2, B3, B4, B8, B11, B12
    """

    blue = patch[0]
    green = patch[1]
    red = patch[2]
    nir = patch[3]

    ndvi_denominator = nir + red

    ndvi = np.divide(
        nir - red,
        ndvi_denominator,
        out=np.zeros_like(nir, dtype=np.float32),
        where=ndvi_denominator != 0
    )

    ndwi_denominator = green + nir

    ndwi = np.divide(
        green - nir,
        ndwi_denominator,
        out=np.zeros_like(green, dtype=np.float32),
        where=ndwi_denominator != 0
    )

    ndvi = np.clip(ndvi, -1.0, 1.0)
    ndwi = np.clip(ndwi, -1.0, 1.0)

    return ndvi, ndwi


def _compute_ndvi_from_tif(tif_path):
    """
    Compute NDVI from a temporal TIFF.
    """

    with rasterio.open(tif_path) as src:
        image = src.read().astype(np.float32)

    image = np.nan_to_num(
        image,
        nan=0.0,
        posinf=0.0,
        neginf=0.0
    )

    red = image[2]
    nir = image[3]

    denominator = nir + red

    ndvi = np.divide(
        nir - red,
        denominator,
        out=np.zeros_like(nir, dtype=np.float32),
        where=denominator != 0
    )

    return np.clip(ndvi, -1.0, 1.0)


def _get_temporal_ndvi(chip_id):
    """
    Get mean NDVI for the corresponding 2020 and 2025 chips.
    """

    chips_2020 = _find_chip_files(2020)
    chips_2025 = _find_chip_files(2025)

    if chip_id not in chips_2020:
        return None, None, None, None

    if chip_id not in chips_2025:
        return None, None, None, None

    ndvi_2020 = _compute_ndvi_from_tif(
        chips_2020[chip_id]
    )

    ndvi_2025 = _compute_ndvi_from_tif(
        chips_2025[chip_id]
    )

    mean_ndvi_2020 = float(
        np.mean(ndvi_2020)
    )

    mean_ndvi_2025 = float(
        np.mean(ndvi_2025)
    )

    difference = abs(
        mean_ndvi_2025 - mean_ndvi_2020
    )

    change_flag = difference > CHANGE_THRESHOLD

    return (
        mean_ndvi_2020,
        mean_ndvi_2025,
        difference,
        change_flag
    )


def classify_imagery(lat, lon, radius_m):
    """
    Classify a satellite image patch and perform
    temporal NDVI change detection.

    Returns a structured dictionary containing:

        latitude
        longitude
        radius_m
        dominant_class
        dominant_class_id
        class_distribution
        confidence
        mean_ndvi
        mean_ndwi
        ndvi_2020
        ndvi_2025
        ndvi_difference
        change_threshold
        change_flag
        inference_time_seconds
    """

    start_time = time.time()

    model = _load_model()

    patch, chip_id, image_path = _get_image_patch(
        lat,
        lon,
        radius_m
    )

    ndvi, ndwi = _compute_ndvi_ndwi(patch)

    image_tensor = torch.from_numpy(
        patch.copy()
    ).float().unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        output = model(image_tensor)

        probabilities = torch.softmax(
            output,
            dim=1
        )

        prediction = torch.argmax(
            probabilities,
            dim=1
        )

    prediction = prediction.squeeze(0).cpu().numpy()

    probability_map = probabilities.squeeze(0).cpu().numpy()

    pixel_count = prediction.size

    class_distribution = {}

    for class_id, class_name in enumerate(CLASS_NAMES):

        pixels = int(
            np.sum(prediction == class_id)
        )

        percentage = (
            pixels / pixel_count
        ) * 100.0

        class_distribution[class_name] = {
            "class_id": class_id,
            "pixels": pixels,
            "percentage": percentage
        }

    class_pixels = np.bincount(
        prediction.ravel(),
        minlength=NUM_CLASSES
    )

    dominant_class_id = int(
        np.argmax(class_pixels)
    )

    dominant_class = CLASS_NAMES[
        dominant_class_id
    ]

    confidence = float(
        np.mean(
            np.max(
                probability_map,
                axis=0
            )
        )
    )

    mean_ndvi = float(
        np.mean(ndvi)
    )

    mean_ndwi = float(
        np.mean(ndwi)
    )

    (
        ndvi_2020,
        ndvi_2025,
        ndvi_difference,
        change_flag
    ) = _get_temporal_ndvi(chip_id)

    inference_time = time.time() - start_time

    return {
        "latitude": float(lat),
        "longitude": float(lon),
        "radius_m": float(radius_m),

        "dominant_class": dominant_class,
        "dominant_class_id": dominant_class_id,

        "class_distribution": class_distribution,

        "confidence": confidence,

        "mean_ndvi": mean_ndvi,
        "mean_ndwi": mean_ndwi,

        "ndvi_2020": ndvi_2020,
        "ndvi_2025": ndvi_2025,
        "ndvi_difference": ndvi_difference,

        "change_threshold": CHANGE_THRESHOLD,
        "change_flag": change_flag,

        "chip_id": chip_id,

        "inference_time_seconds": inference_time
    }
