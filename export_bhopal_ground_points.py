
from pathlib import Path
import json

import laspy
import numpy as np
from pyproj import Transformer


# ============================================================
# GeoSense Agent — Bhopal Public Terrain Data Export
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

LAS_PATH = (
    PROJECT_ROOT
    / "data"
    / "satellite"
    / "point_cloud_full.las"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "frontend"
    / "digital_twin"
    / "digital_twin_app"
    / "public"
    / "data"
)

NPZ_FILE = OUTPUT_DIR / "bhopal_ground_points.npz"
BIN_FILE = OUTPUT_DIR / "bhopal_ground_points.bin"
METADATA_FILE = OUTPUT_DIR / "bhopal_ground_metadata.json"


def main():
    print("=" * 60)
    print("GeoSense Agent — Bhopal Terrain Export")
    print("=" * 60)

    if not LAS_PATH.exists():
        raise FileNotFoundError(
            f"LAS file not found: {LAS_PATH}"
        )

    print("\nLoading drone LAS file...")

    las = laspy.read(LAS_PATH)

    ground_mask = np.asarray(las.classification) == 2

    if not np.any(ground_mask):
        raise ValueError(
            "No ground-classified points (LAS class 2) found."
        )

    print("Extracting ground points...")

    x = np.asarray(
        las.x[ground_mask],
        dtype=np.float64
    )

    y = np.asarray(
        las.y[ground_mask],
        dtype=np.float64
    )

    z = np.asarray(
        las.z[ground_mask],
        dtype=np.float32
    )

    if len(x) < 10:
        raise ValueError(
            "Insufficient ground points."
        )

    print("Converting EPSG:32643 to WGS84...")

    transformer = Transformer.from_crs(
        "EPSG:32643",
        "EPSG:4326",
        always_xy=True,
    )

    longitude, latitude = transformer.transform(x, y)

    # Browser dataset format:
    # Each point contains three little-endian float32 values:
    # latitude, longitude, elevation in metres.

    points = np.empty(
        (len(x), 3),
        dtype="<f4"
    )

    points[:, 0] = latitude
    points[:, 1] = longitude
    points[:, 2] = z

    if not np.all(np.isfinite(points)):
        raise ValueError(
            "Export contains invalid coordinate or elevation values."
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\nWriting compressed NPZ dataset...")

    np.savez_compressed(
        NPZ_FILE,
        points=points,
    )

    print("Writing browser-readable binary dataset...")

    points.tofile(BIN_FILE)

    metadata = {
        "project": "GeoSense Agent",
        "study_area": "Bhopal, Madhya Pradesh, India",
        "data_source": "Bhopal drone survey LAS",
        "classification": 2,
        "source_crs": "EPSG:32643",
        "coordinate_crs": "EPSG:4326",
        "point_count": int(len(points)),
        "binary_file": "bhopal_ground_points.bin",
        "binary_format": "float32 little-endian",
        "values_per_point": [
            "latitude",
            "longitude",
            "ground_elevation_m"
        ],
        "bytes_per_point": 12,
        "analysis_method": (
            "Nearest classified ground point"
        ),
        "limitation": (
            "Not a flood-risk prediction or continuous terrain model."
        ),
        "latitude_min": float(np.min(latitude)),
        "latitude_max": float(np.max(latitude)),
        "longitude_min": float(np.min(longitude)),
        "longitude_max": float(np.max(longitude)),
        "elevation_min_m": float(np.min(z)),
        "elevation_max_m": float(np.max(z)),
    }

    METADATA_FILE.write_text(
        json.dumps(metadata, indent=4),
        encoding="utf-8"
    )

    print("\n" + "=" * 60)
    print("BHOPAL TERRAIN EXPORT SUCCESSFUL")
    print("=" * 60)

    print("Ground points:", len(points))

    print(
        "NPZ size (MB):",
        round(NPZ_FILE.stat().st_size / 1024**2, 2)
    )

    print(
        "Binary size (MB):",
        round(BIN_FILE.stat().st_size / 1024**2, 2)
    )

    print("NPZ:", NPZ_FILE)
    print("Binary:", BIN_FILE)
    print("Metadata:", METADATA_FILE)

    print("\nElevation range:")
    print(
        round(float(np.min(z)), 3),
        "m to",
        round(float(np.max(z)), 3),
        "m"
    )

    print("\nAll files generated successfully.")


if __name__ == "__main__":
    main()
