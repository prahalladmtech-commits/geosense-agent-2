from pathlib import Path
import csv
from PIL import Image
import numpy as np


IMAGE_DIR = Path("data/streetview/images")
RESULT_DIR = Path("data/streetview/results")
RESULT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RESULT_DIR / "streetview_features.csv"


def calculate_features(image_path):
    image = Image.open(image_path).convert("RGB")
    array = np.asarray(image, dtype=np.float32)

    red = array[:, :, 0]
    green = array[:, :, 1]
    blue = array[:, :, 2]

    # Basic colour features
    mean_r = np.mean(red)
    mean_g = np.mean(green)
    mean_b = np.mean(blue)

    # Green vegetation indicator
    green_ratio = np.mean(green > red)

    # Brightness
    brightness = np.mean(array)

    # Image dimensions
    height, width = array.shape[:2]

    return {
        "filename": image_path.name,
        "width": width,
        "height": height,
        "mean_r": round(float(mean_r), 2),
        "mean_g": round(float(mean_g), 2),
        "mean_b": round(float(mean_b), 2),
        "brightness": round(float(brightness), 2),
        "green_ratio": round(float(green_ratio), 4),
    }


if __name__ == "__main__":

    images = sorted(IMAGE_DIR.glob("*.jpg"))

    print(f"Found {len(images)} images")

    features = []

    for image_path in images:
        result = calculate_features(image_path)
        features.append(result)

        print(
            f"{image_path.name}: "
            f"brightness={result['brightness']:.2f}, "
            f"green_ratio={result['green_ratio']:.4f}"
        )

    fieldnames = [
        "filename",
        "width",
        "height",
        "mean_r",
        "mean_g",
        "mean_b",
        "brightness",
        "green_ratio",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(features)

    print("\nFeature extraction completed.")
    print(f"Saved to: {OUTPUT_FILE}")