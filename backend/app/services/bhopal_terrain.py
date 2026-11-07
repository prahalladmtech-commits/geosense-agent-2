from pathlib import Path

import laspy
import numpy as np
from pyproj import Transformer
from scipy.spatial import cKDTree


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LAS_PATH = PROJECT_ROOT / "data" / "satellite" / "point_cloud_full.las"

# Drone survey CRS: WGS 84 / UTM Zone 43N
TO_UTM = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32643",
    always_xy=True
)

_tree = None
_ground_z = None


def load_ground_points():
    global _tree, _ground_z

    if _tree is not None:
        return

    if not LAS_PATH.exists():
        raise FileNotFoundError(
            f"Bhopal drone point cloud not found: {LAS_PATH}"
        )

    las = laspy.read(LAS_PATH)

    ground_mask = las.classification == 2

    if not np.any(ground_mask):
        raise ValueError("No ground-classified points (LAS class 2) found.")

    x = np.asarray(las.x[ground_mask], dtype=np.float64)
    y = np.asarray(las.y[ground_mask], dtype=np.float64)
    z = np.asarray(las.z[ground_mask], dtype=np.float64)

    if len(x) < 10:
        raise ValueError("Insufficient ground points for terrain analysis.")

    _tree = cKDTree(np.column_stack((x, y)))
    _ground_z = z


def analyze_bhopal_location(latitude: float, longitude: float):
    load_ground_points()

    x, y = TO_UTM.transform(longitude, latitude)

    distance, index = _tree.query([x, y], k=1)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "ground_elevation_m": round(float(_ground_z[index]), 3),
        "nearest_ground_point_distance_m": round(float(distance), 3),
        "ground_points_used": int(len(_ground_z)),
        "data_source": "Bhopal drone survey LAS, LAS classification 2",
        "crs": "EPSG:32643",
        "analysis": "Nearest classified ground point; not a flood-risk prediction"
    }