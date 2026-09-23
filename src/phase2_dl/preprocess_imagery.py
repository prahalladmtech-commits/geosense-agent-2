import os
import glob
import numpy as np
import rasterio
from rasterio.merge import merge


# ============================================================
# Directories
# ============================================================

RAW_DIR = "data/satellite/raw"
PROCESSED_DIR = "data/satellite/processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)


# ============================================================
# Sentinel-2 bands used by GeoSense
# ============================================================
#
# B2  = Blue
# B3  = Green
# B4  = Red
# B8  = NIR
# B11 = SWIR1
# B12 = SWIR2
#
# These six bands are used as the 6-channel input
# for the Phase 2 U-Net.
# ============================================================

BAND_NAMES = [
    "B2",
    "B3",
    "B4",
    "B8",
    "B11",
    "B12"
]


# ============================================================
# Find files
# ============================================================

def get_tile_files(year):

    pattern = os.path.join(
        RAW_DIR,
        f"sentinel2_kolkata_{year}_tile_*.tif"
    )

    files = sorted(glob.glob(pattern))

    print(f"\nYear: {year}")
    print(f"Tiles found: {len(files)}")

    return files


# ============================================================
# Mosaic 16 tiles
# ============================================================

def create_mosaic(year):

    files = get_tile_files(year)

    if len(files) != 16:

        raise RuntimeError(
            f"Expected 16 tiles for {year}, "
            f"but found {len(files)}."
        )

    print(f"Creating {year} mosaic...")

    src_files = []

    try:

        for file in files:

            src = rasterio.open(file)
            src_files.append(src)

        mosaic, transform = merge(src_files)

        # ----------------------------------------------------
        # Copy metadata from first tile
        # ----------------------------------------------------

        meta = src_files[0].meta.copy()

        meta.update(
            {
                "driver": "GTiff",
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": transform,
                "compress": "deflate"
            }
        )

        output_file = os.path.join(
            PROCESSED_DIR,
            f"sentinel2_kolkata_{year}_mosaic.tif"
        )

        with rasterio.open(
            output_file,
            "w",
            **meta
        ) as dst:

            dst.write(mosaic)

        print(
            f"Mosaic created: {output_file}"
        )

        print(
            f"Mosaic shape: {mosaic.shape}"
        )

        return output_file

    finally:

        for src in src_files:

            src.close()


# ============================================================
# Preprocess Sentinel-2 image
# ============================================================

def preprocess_image(year, mosaic_file):

    print("\n" + "=" * 60)
    print(f"Preprocessing {year}")
    print("=" * 60)

    output_file = os.path.join(
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

    metadata_file = os.path.join(
        PROCESSED_DIR,
        f"metadata_kolkata_{year}.txt"
    )

    # --------------------------------------------------------
    # Read mosaic
    # --------------------------------------------------------

    with rasterio.open(mosaic_file) as src:

        data = src.read().astype(np.float32)

        profile = src.profile.copy()

        transform = src.transform

        crs = src.crs

        width = src.width
        height = src.height

        count = src.count

    print(f"Input bands: {count}")
    print(f"Image size: {width} x {height}")

    # --------------------------------------------------------
    # Sentinel-2 exported image normally contains the
    # Sentinel-2 bands in the following order:
    #
    # B1, B2, B3, B4, B5, B6, B7, B8, B8A, B9, B11, B12
    #
    # We need:
    # B2, B3, B4, B8, B11, B12
    # --------------------------------------------------------

    if count < 12:

        raise RuntimeError(
            f"Expected at least 12 Sentinel-2 bands, "
            f"but found {count}."
        )

    selected = np.stack(
        [
            data[1],   # B2
            data[2],   # B3
            data[3],   # B4
            data[7],   # B8
            data[10],  # B11
            data[11]   # B12
        ]
    )

    # --------------------------------------------------------
    # Convert invalid values to NaN
    # --------------------------------------------------------

    selected[selected <= 0] = np.nan

    # --------------------------------------------------------
    # Cloud flag
    #
    # Manual rule:
    # pixel is considered cloud when all selected bands
    # have values > 3000.
    # --------------------------------------------------------

    cloud_mask = np.all(
        selected > 3000,
        axis=0
    )

    print(
        "Cloud pixels:",
        int(np.sum(cloud_mask))
    )

    selected[:, cloud_mask] = np.nan

    # --------------------------------------------------------
    # Normalize Sentinel-2 reflectance
    #
    # Sentinel-2 surface reflectance:
    # 0-10000
    #
    # Normalize:
    # value / 10000
    #
    # Clip:
    # 0-1
    # --------------------------------------------------------

    normalized = selected / 10000.0

    normalized = np.clip(
        normalized,
        0.0,
        1.0
    )

    # --------------------------------------------------------
    # NDVI
    #
    # NDVI = (NIR - RED) / (NIR + RED)
    #
    # B8 = NIR
    # B4 = RED
    # --------------------------------------------------------

    nir = normalized[3]
    red = normalized[2]

    ndvi = (
        (nir - red) /
        (nir + red + 1e-10)
    )

    # --------------------------------------------------------
    # NDWI
    #
    # NDWI = (GREEN - NIR) / (GREEN + NIR)
    #
    # B3 = GREEN
    # B8 = NIR
    # --------------------------------------------------------

    green = normalized[1]

    ndwi = (
        (green - nir) /
        (green + nir + 1e-10)
    )

    # --------------------------------------------------------
    # Save six-band clean image
    # --------------------------------------------------------

    clean_profile = profile.copy()

    clean_profile.update(
        {
            "driver": "GTiff",
            "dtype": "float32",
            "count": 6,
            "height": height,
            "width": width,
            "transform": transform,
            "crs": crs,
            "compress": "deflate",
            "nodata": np.nan
        }
    )

    with rasterio.open(
        output_file,
        "w",
        **clean_profile
    ) as dst:

        dst.write(
            normalized.astype(
                np.float32
            )
        )

        dst.set_band_description(
            1,
            "B2_Blue"
        )

        dst.set_band_description(
            2,
            "B3_Green"
        )

        dst.set_band_description(
            3,
            "B4_Red"
        )

        dst.set_band_description(
            4,
            "B8_NIR"
        )

        dst.set_band_description(
            5,
            "B11_SWIR1"
        )

        dst.set_band_description(
            6,
            "B12_SWIR2"
        )

    print(
        f"Clean image saved: {output_file}"
    )

    # --------------------------------------------------------
    # Save NDVI
    # --------------------------------------------------------

    index_profile = profile.copy()

    index_profile.update(
        {
            "driver": "GTiff",
            "dtype": "float32",
            "count": 1,
            "height": height,
            "width": width,
            "transform": transform,
            "crs": crs,
            "compress": "deflate",
            "nodata": np.nan
        }
    )

    with rasterio.open(
        ndvi_file,
        "w",
        **index_profile
    ) as dst:

        dst.write(
            ndvi.astype(np.float32),
            1
        )

        dst.set_band_description(
            1,
            "NDVI"
        )

    print(
        f"NDVI saved: {ndvi_file}"
    )

    # --------------------------------------------------------
    # Save NDWI
    # --------------------------------------------------------

    with rasterio.open(
        ndwi_file,
        "w",
        **index_profile
    ) as dst:

        dst.write(
            ndwi.astype(np.float32),
            1
        )

        dst.set_band_description(
            1,
            "NDWI"
        )

    print(
        f"NDWI saved: {ndwi_file}"
    )

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    valid_pixels = np.sum(
        ~np.isnan(normalized[0])
    )

    total_pixels = (
        normalized.shape[1] *
        normalized.shape[2]
    )

    cloud_percentage = (
        np.sum(cloud_mask) /
        total_pixels *
        100
    )

    with open(
        metadata_file,
        "w"
    ) as f:

        f.write(
            f"Year: {year}\n"
        )

        f.write(
            f"Image width: {width}\n"
        )

        f.write(
            f"Image height: {height}\n"
        )

        f.write(
            f"Input bands: {count}\n"
        )

        f.write(
            "Output bands: B2, B3, B4, B8, B11, B12\n"
        )

        f.write(
            f"Cloud pixels: {np.sum(cloud_mask)}\n"
        )

        f.write(
            f"Cloud percentage: "
            f"{cloud_percentage:.4f}%\n"
        )

        f.write(
            f"Valid pixels: {valid_pixels}\n"
        )

        f.write(
            f"Total pixels: {total_pixels}\n"
        )

        f.write(
            f"CRS: {crs}\n"
        )

        f.write(
            "Normalization: reflectance / 10000\n"
        )

        f.write(
            "NDVI = (B8 - B4) / (B8 + B4)\n"
        )

        f.write(
            "NDWI = (B3 - B8) / (B3 + B8)\n"
        )

    print(
        f"Metadata saved: {metadata_file}"
    )


# ============================================================
# Main program
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("GeoSense Agent 2.0")
    print("Exercise 2.2 - Sentinel-2 Preprocessing")
    print("Study Area: Kolkata")
    print("Years: 2020 and 2025")
    print("=" * 60)

    # --------------------------------------------------------
    # 2020
    # --------------------------------------------------------

    mosaic_2020 = create_mosaic(2020)

    preprocess_image(
        2020,
        mosaic_2020
    )

    # --------------------------------------------------------
    # 2025
    # --------------------------------------------------------

    mosaic_2025 = create_mosaic(2025)

    preprocess_image(
        2025,
        mosaic_2025
    )

    print("\n" + "=" * 60)
    print("Exercise 2.2 preprocessing completed.")
    print("=" * 60)