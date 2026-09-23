import os
import numpy as np
import rasterio


# ============================================================
# Directories
# ============================================================

PROCESSED_DIR = "data/satellite/processed"
CHIP_DIR = "data/satellite/chips"

os.makedirs(CHIP_DIR, exist_ok=True)


# ============================================================
# Chipping parameters
# ============================================================

CHIP_SIZE = 224
STRIDE = 174

MAX_NAN_RATIO = 0.20


# ============================================================
# Chip one image
# ============================================================

def chip_image(year):

    input_file = os.path.join(
        PROCESSED_DIR,
        f"sentinel2_kolkata_{year}_clean.tif"
    )

    year_dir = os.path.join(
        CHIP_DIR,
        str(year)
    )

    os.makedirs(
        year_dir,
        exist_ok=True
    )

    print("\n" + "=" * 60)
    print(f"Chipping Sentinel-2 image: {year}")
    print("=" * 60)

    with rasterio.open(input_file) as src:

        data = src.read().astype(
            np.float32
        )

        profile = src.profile.copy()

        height = src.height
        width = src.width

        transform = src.transform

    print(
        f"Image size: {width} x {height}"
    )

    print(
        f"Chip size: {CHIP_SIZE} x {CHIP_SIZE}"
    )

    print(
        f"Stride: {STRIDE}"
    )

    chip_count = 0
    skipped_count = 0

    # --------------------------------------------------------
    # Band means
    # --------------------------------------------------------

    band_means = np.nanmean(
        data,
        axis=(1, 2)
    )

    print(
        "Band means:",
        band_means
    )

    # --------------------------------------------------------
    # Sliding window
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

            chip = data[
                :,
                row:row + CHIP_SIZE,
                col:col + CHIP_SIZE
            ].copy()

            # ------------------------------------------------
            # Calculate NaN ratio
            # ------------------------------------------------

            nan_ratio = np.isnan(
                chip
            ).mean()

            # ------------------------------------------------
            # Skip if >20% NaN
            # ------------------------------------------------

            if nan_ratio > MAX_NAN_RATIO:

                skipped_count += 1

                continue

            # ------------------------------------------------
            # Fill remaining NaN values
            # with corresponding band mean
            # ------------------------------------------------

            for band in range(
                chip.shape[0]
            ):

                nan_mask = np.isnan(
                    chip[band]
                )

                if np.any(nan_mask):

                    chip[band][nan_mask] = (
                        band_means[band]
                    )

            # ------------------------------------------------
            # Output filename
            # ------------------------------------------------

            chip_count += 1

            output_file = os.path.join(
                year_dir,
                f"chip_{chip_count:05d}.tif"
            )

            # ------------------------------------------------
            # Chip profile
            # ------------------------------------------------

            chip_transform = rasterio.windows.transform(
                rasterio.windows.Window(
                    col,
                    row,
                    CHIP_SIZE,
                    CHIP_SIZE
                ),
                transform
            )

            chip_profile = profile.copy()

            chip_profile.update(
                {
                    "driver": "GTiff",
                    "height": CHIP_SIZE,
                    "width": CHIP_SIZE,
                    "count": data.shape[0],
                    "dtype": "float32",
                    "transform": chip_transform,
                    "compress": "deflate",
                    "nodata": None
                }
            )

            # ------------------------------------------------
            # Save chip
            # ------------------------------------------------

            with rasterio.open(
                output_file,
                "w",
                **chip_profile
            ) as dst:

                dst.write(
                    chip.astype(
                        np.float32
                    )
                )

    print(
        f"\nValid chips: {chip_count}"
    )

    print(
        f"Skipped chips: {skipped_count}"
    )

    print(
        f"Saved to: {year_dir}"
    )


# ============================================================
# Main program
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("GeoSense Agent 2.0")
    print("Exercise 2.3 - Image Chipping")
    print("Study Area: Kolkata")
    print("Years: 2020 and 2025")
    print("=" * 60)

    chip_image(2020)

    chip_image(2025)

    print("\n" + "=" * 60)
    print("Exercise 2.3 completed.")
    print("=" * 60)