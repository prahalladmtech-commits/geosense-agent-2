import os
import ee
import geemap

# ============================================================
# Google Earth Engine
# ============================================================

PROJECT_ID = "certain-art-478214-k7"

ee.Initialize(project=PROJECT_ID)

# ============================================================
# Study Area - Kolkata
# ============================================================

BBOX = [88.30, 22.45, 88.42, 22.67]

STUDY_AREA = ee.Geometry.Rectangle(BBOX)

# ============================================================
# Output directory
# ============================================================

OUTPUT_DIR = "data/satellite/raw"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# Get Sentinel-2 composite
# ============================================================

def get_clean_image(year):

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(STUDY_AREA)
        .filterDate(start_date, end_date)
        .filter(
            ee.Filter.lt(
                "CLOUDY_PIXEL_PERCENTAGE",
                10
            )
        )
    )

    count = collection.size().getInfo()

    print(f"\nYear: {year}")
    print(f"Images found: {count}")

    if count == 0:
        print(f"No Sentinel-2 images found for {year}.")
        return None

    image = collection.median().clip(STUDY_AREA)

    return image


# ============================================================
# Download one year using 4 x 4 tiles
# ============================================================

def download_year(year):

    image = get_clean_image(year)

    if image is None:
        return

    min_lon, min_lat, max_lon, max_lat = BBOX

    # --------------------------------------------------------
    # Divide longitude and latitude into 4 sections
    # --------------------------------------------------------

    lon_step = (max_lon - min_lon) / 4
    lat_step = (max_lat - min_lat) / 4

    tile_number = 1

    # --------------------------------------------------------
    # Create 16 tiles
    # --------------------------------------------------------

    for row in range(4):

        for col in range(4):

            tile_min_lon = min_lon + col * lon_step
            tile_max_lon = min_lon + (col + 1) * lon_step

            tile_min_lat = min_lat + row * lat_step
            tile_max_lat = min_lat + (row + 1) * lat_step

            coords = [
                tile_min_lon,
                tile_min_lat,
                tile_max_lon,
                tile_max_lat
            ]

            tile_name = f"tile_{tile_number:02d}"

            print("\n" + "=" * 60)
            print(f"Downloading {year} - {tile_name}")
            print(f"Bounds: {coords}")
            print("=" * 60)

            region = ee.Geometry.Rectangle(coords)

            output_file = os.path.join(
                OUTPUT_DIR,
                f"sentinel2_kolkata_{year}_{tile_name}.tif"
            )

            print(f"Output: {output_file}")

            try:

                geemap.ee_export_image(
                    image,
                    filename=output_file,
                    scale=10,
                    region=region,
                    file_per_band=False
                )

                # ------------------------------------------------
                # Verify file
                # ------------------------------------------------

                if os.path.exists(output_file):

                    size_mb = (
                        os.path.getsize(output_file)
                        / (1024 * 1024)
                    )

                    if size_mb > 0:

                        print(
                            f"Finished {year} {tile_name}: "
                            f"{size_mb:.2f} MB"
                        )

                    else:

                        print(
                            f"ERROR: {output_file} is empty."
                        )

                else:

                    print(
                        f"ERROR: {output_file} "
                        f"was not created."
                    )

            except Exception as e:

                print(
                    f"ERROR downloading "
                    f"{year} {tile_name}:"
                )

                print(e)

            tile_number += 1


# ============================================================
# Main program
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("GeoSense Agent 2.0")
    print("Exercise 2.1 - Sentinel-2 Data Acquisition")
    print("Study Area: Kolkata")
    print("Years: 2020 and 2025")
    print("Download grid: 4 x 4 = 16 tiles per year")
    print("=" * 60)

    # --------------------------------------------------------
    # Download 2020
    # --------------------------------------------------------

    download_year(2020)

    # --------------------------------------------------------
    # Download 2025
    # --------------------------------------------------------

    download_year(2025)

    print("\n" + "=" * 60)
    print("All download processes finished.")
    print("=" * 60)