import os
import numpy as np
import rasterio


# ============================================================
# Directories
# ============================================================

LABEL_DIR = "data/satellite/labels"
CHIP_DIR = "data/satellite/label_chips"

os.makedirs(CHIP_DIR, exist_ok=True)


# ============================================================
# Chipping parameters
# ============================================================

CHIP_SIZE = 224
STRIDE = 174

IGNORE_LABEL = 255


# ============================================================
# Chip labels
# ============================================================

def chip_labels(year):

    input_file = os.path.join(
        LABEL_DIR,
        f"labels_kolkata_{year}.tif"
    )

    output_dir = os.path.join(
        CHIP_DIR,
        str(year)
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    print("\n" + "=" * 60)
    print(f"Chipping labels: {year}")
    print("=" * 60)

    with rasterio.open(input_file) as src:

        labels = src.read(1)

        height = src.height
        width = src.width

    print(
        f"Label image size: "
        f"{width} x {height}"
    )

    chip_count = 0

    # --------------------------------------------------------
    # Same sliding window used for image chips
    # --------------------------------------------------------

    for row in range(
        0,
        height - CHIP_SIZE + 1,
        STRIDE
    ):

        for col in range(
            0,
            width - CHIP_SIZE + 1,
            STRIDE
        ):

            chip = labels[
                row:row + CHIP_SIZE,
                col:col + CHIP_SIZE
            ]

            chip_count += 1

            output_file = os.path.join(
                output_dir,
                f"label_{chip_count:05d}.npy"
            )

            np.save(
                output_file,
                chip.astype(np.uint8)
            )

    print(
        f"Label chips created: {chip_count}"
    )

    print(
        f"Saved to: {output_dir}"
    )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("GeoSense Agent 2.0")
    print("Exercise 3 - Label Chipping")
    print("Years: 2020 and 2025")
    print("=" * 60)

    chip_labels(2020)

    chip_labels(2025)

    print("\n" + "=" * 60)
    print("Label chipping completed.")
    print("=" * 60)