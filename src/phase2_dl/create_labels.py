import os
import numpy as np
import rasterio


# ============================================================
# Directories
# ============================================================

PROCESSED_DIR = "data/satellite/processed"
LABEL_DIR = "data/satellite/labels"

os.makedirs(LABEL_DIR, exist_ok=True)


# ============================================================
# Class definitions
# ============================================================

URBAN = 0
VEGETATION = 1
WATER = 2
BARE_LAND = 3
AGRICULTURE = 4


CLASS_NAMES = {
    0: "Urban",
    1: "Vegetation",
    2: "Water",
    3: "Bare Land",
    4: "Agriculture"
}


# ============================================================
# Generate labels
# ============================================================

def create_labels(year):

    clean_file = os.path.join(
        PROCESSED_DIR,
        f"sentinel2_kolkata_{year}_clean.tif"
    )

    ndvi_file = os.path.join(
        PROCESSED_DIR,
        f"ndvi_kolkata_{year}.tif"
    )

    ndwi_file = os.path.join(
        PROCESSED_DIR,
        f"ndwi_kolkata_{year}.tif"
    )

    output_file = os.path.join(
        LABEL_DIR,
        f"labels_kolkata_{year}.tif"
    )

    print("\n" + "=" * 60)
    print(f"Generating pseudo-labels: {year}")
    print("=" * 60)

    # --------------------------------------------------------
    # Read clean image
    # --------------------------------------------------------

    with rasterio.open(clean_file) as src:

        image = src.read().astype(
            np.float32
        )

        profile = src.profile.copy()

    # --------------------------------------------------------
    # Read NDVI
    # --------------------------------------------------------

    with rasterio.open(ndvi_file) as src:

        ndvi = src.read(1).astype(
            np.float32
        )

    # --------------------------------------------------------
    # Read NDWI
    # --------------------------------------------------------

    with rasterio.open(ndwi_file) as src:

        ndwi = src.read(1).astype(
            np.float32
        )

    # --------------------------------------------------------
    # SWIR1 = B11
    #
    # Clean image bands:
    # 1 = B2
    # 2 = B3
    # 3 = B4
    # 4 = B8
    # 5 = B11
    # 6 = B12
    # --------------------------------------------------------

    swir = image[4]

    # --------------------------------------------------------
    # Initialize all pixels as Bare Land
    # --------------------------------------------------------

    labels = np.full(
        ndvi.shape,
        BARE_LAND,
        dtype=np.uint8
    )

    # --------------------------------------------------------
    # Valid pixels
    # --------------------------------------------------------

    valid = (
        np.isfinite(ndvi) &
        np.isfinite(ndwi) &
        np.isfinite(swir)
    )

    # --------------------------------------------------------
    # Rule 1: Water
    # --------------------------------------------------------

    water = (
        valid &
        (ndwi > 0.30)
    )

    labels[water] = WATER

    # --------------------------------------------------------
    # Rule 2: Vegetation
    # --------------------------------------------------------

    vegetation = (
        valid &
        ~water &
        (ndvi > 0.40)
    )

    labels[vegetation] = VEGETATION

    # --------------------------------------------------------
    # Rule 3: Agriculture
    # --------------------------------------------------------

    agriculture = (
        valid &
        ~water &
        ~vegetation &
        (ndvi > 0.15)
    )

    labels[agriculture] = AGRICULTURE

    # --------------------------------------------------------
    # Rule 4: Urban
    # --------------------------------------------------------

    urban = (
        valid &
        ~water &
        ~vegetation &
        ~agriculture &
        (ndvi < 0.05) &
        (swir > 0.20)
    )

    labels[urban] = URBAN

    # --------------------------------------------------------
    # Invalid pixels
    #
    # Use 255 as ignore/no-data label.
    # --------------------------------------------------------

    labels[~valid] = 255

    # --------------------------------------------------------
    # Save labels
    # --------------------------------------------------------

    profile.update(
        {
            "driver": "GTiff",
            "dtype": "uint8",
            "count": 1,
            "nodata": 255,
            "compress": "deflate"
        }
    )

    with rasterio.open(
        output_file,
        "w",
        **profile
    ) as dst:

        dst.write(
            labels,
            1
        )

        dst.set_band_description(
            1,
            "Land Cover Class"
        )

    print(
        f"Labels saved: {output_file}"
    )

    # --------------------------------------------------------
    # Print class statistics
    # --------------------------------------------------------

    print("\nClass statistics:")

    total_valid = np.sum(
        labels != 255
    )

    for class_id, class_name in CLASS_NAMES.items():

        count = np.sum(
            labels == class_id
        )

        percentage = (
            count / total_valid * 100
            if total_valid > 0
            else 0
        )

        print(
            f"{class_id} - {class_name}: "
            f"{count:,} pixels "
            f"({percentage:.2f}%)"
        )

    print(
        f"Valid pixels: {total_valid:,}"
    )

    print(
        f"Invalid pixels: "
        f"{np.sum(labels == 255):,}"
    )


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("GeoSense Agent 2.0")
    print("Exercise 3 - Ground Truth Generation")
    print("Study Area: Kolkata")
    print("Years: 2020 and 2025")
    print("=" * 60)

    create_labels(2020)

    create_labels(2025)

    print("\n" + "=" * 60)
    print("Pseudo-label generation completed.")
    print("=" * 60)