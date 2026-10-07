from pathlib import Path
import pandas as pd


LIDAR_DIR = Path("data/lidar/processed")
STREETVIEW_FILE = Path("data/streetview/results/streetview_features.csv")
OUTPUT_DIR = Path("data/streetview/results")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "multimodal_features.csv"


# Read street-view features
streetview = pd.read_csv(STREETVIEW_FILE)


# LiDAR summary features
lidar_features = {
    "lidar_dem_min": None,
    "lidar_dem_max": None,
    "lidar_dem_mean": None,
    "lidar_resolution": None,
}


# Read LiDAR DEM statistics
import rasterio

dem_file = LIDAR_DIR / "autzen_dem.tif"

with rasterio.open(dem_file) as src:
    dem = src.read(1)
    valid = dem[dem != src.nodata]

    lidar_features["lidar_dem_min"] = round(float(valid.min()), 2)
    lidar_features["lidar_dem_max"] = round(float(valid.max()), 2)
    lidar_features["lidar_dem_mean"] = round(float(valid.mean()), 2)
    lidar_features["lidar_resolution"] = round(float(src.res[0]), 2)


# Repeat LiDAR summary values for each street-view image
for key, value in lidar_features.items():
    streetview[key] = value


# Save fused dataset
streetview.to_csv(OUTPUT_FILE, index=False)

print("Multimodal feature fusion completed.")
print(f"Images/features: {len(streetview)}")
print(f"Saved to: {OUTPUT_FILE}")