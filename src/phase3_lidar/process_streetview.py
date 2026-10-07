from pathlib import Path

from PIL import Image
import numpy as np


IMAGE_DIR = Path("data/streetview/images")
RESULT_DIR = Path("data/streetview/results")
RESULT_DIR.mkdir(parents=True, exist_ok=True)


def process_image(image_path):
    """Read an image and calculate basic image statistics."""

    image = Image.open(image_path).convert("RGB")
    array = np.asarray(image)

    height, width = array.shape[:2]

    mean_rgb = array.mean(axis=(0, 1))
    min_value = array.min()
    max_value = array.max()

    print(f"\nImage: {image_path.name}")
    print(f"Size: {width} x {height}")
    print(
        f"Mean RGB: "
        f"{mean_rgb[0]:.2f}, "
        f"{mean_rgb[1]:.2f}, "
        f"{mean_rgb[2]:.2f}"
    )
    print(f"Pixel range: {min_value} - {max_value}")

    return {
        "filename": image_path.name,
        "width": width,
        "height": height,
        "mean_r": mean_rgb[0],
        "mean_g": mean_rgb[1],
        "mean_b": mean_rgb[2],
    }


if __name__ == "__main__":

    images = sorted(IMAGE_DIR.glob("*.jpg"))

    print(f"Found {len(images)} street images")

    results = []

    for image_path in images:
        results.append(process_image(image_path))

    output_file = RESULT_DIR / "streetview_image_statistics.csv"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("filename,width,height,mean_r,mean_g,mean_b\n")

        for item in results:
            f.write(
                f"{item['filename']},"
                f"{item['width']},"
                f"{item['height']},"
                f"{item['mean_r']:.2f},"
                f"{item['mean_g']:.2f},"
                f"{item['mean_b']:.2f}\n"
            )

    print("\nProcessing completed.")
    print(f"Results saved to: {output_file}")