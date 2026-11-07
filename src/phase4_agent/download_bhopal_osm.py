
from pathlib import Path
import time
import sys
import traceback

import osmnx as ox
import geopandas as gpd
import pandas as pd

# --------------------------------------------------
# 1. PROJECT SETTINGS
# --------------------------------------------------

PROJECT_DIR = Path(r"C:\GeoSense_Agent")

OUTPUT_DIR = PROJECT_DIR / "data" / "satellite" / "bhopal_osm"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STUDY_AREA = "Bhopal, Madhya Pradesh, India"

# Separate output files: Kolkata data remains untouched.
BOUNDARY_FILE = OUTPUT_DIR / "bhopal_boundary.geojson"
ROADS_FILE = OUTPUT_DIR / "bhopal_roads.gpkg"
HOSPITALS_FILE = OUTPUT_DIR / "bhopal_hospitals.gpkg"
SUMMARY_FILE = OUTPUT_DIR / "download_summary.txt"

# --------------------------------------------------
# 2. OVERPASS CONFIGURATION
# --------------------------------------------------

ox.settings.overpass_url = "https://overpass.kumi.systems/api"
ox.settings.timeout = 180
ox.settings.use_cache = True
ox.settings.log_console = True

print("=" * 60)
print("GEOSENSE PHASE 4 - BHOPAL OSM DATA DOWNLOAD")
print("=" * 60)
print("Study area:", STUDY_AREA)
print("Output folder:", OUTPUT_DIR)
print("Overpass endpoint:", ox.settings.overpass_url)

# --------------------------------------------------
# 3. RETRY HELPER
# --------------------------------------------------

def run_with_retries(description, function, attempts=3):
    """Retry a download after temporary network/server errors."""

    last_error = None

    for attempt in range(1, attempts + 1):
        try:
            print(
                f"\n{description}: "
                f"attempt {attempt}/{attempts}"
            )

            result = function()

            if result is None or len(result) == 0:
                raise RuntimeError(
                    f"{description} returned no features."
                )

            print(f"{description} completed.")
            return result

        except Exception as exc:
            last_error = exc

            print(
                f"{description} failed: "
                f"{type(exc).__name__}: {exc}"
            )

            if attempt < attempts:
                wait_seconds = attempt * 15
                print(f"Retrying in {wait_seconds} seconds...")
                time.sleep(wait_seconds)

    raise RuntimeError(
        f"{description} failed after {attempts} attempts."
    ) from last_error


# --------------------------------------------------
# 4. DOWNLOAD BHOPAL STUDY-AREA BOUNDARY
# --------------------------------------------------

def download_boundary():
    boundary = run_with_retries(
        "Downloading Bhopal boundary",
        lambda: ox.geocode_to_gdf(STUDY_AREA),
    )

    if boundary.crs is None:
        raise RuntimeError("Boundary CRS is missing.")

    boundary = boundary.to_crs("EPSG:4326")
    boundary.to_file(BOUNDARY_FILE, driver="GeoJSON")

    print("Boundary saved:", BOUNDARY_FILE)
    print("Boundary CRS:", boundary.crs)
    print("Boundary bounds:", boundary.total_bounds)

    return boundary


# --------------------------------------------------
# 5. DOWNLOAD ROAD NETWORK
# --------------------------------------------------

def download_roads(boundary):
    polygon = boundary.geometry.union_all()

    graph = run_with_retries(
        "Downloading Bhopal road network",
        lambda: ox.graph.graph_from_polygon(
            polygon,
            network_type="drive",
            simplify=True,
            retain_all=True,
            truncate_by_edge=True,
        ),
    )

    roads = ox.convert.graph_to_gdfs(
        graph,
        nodes=False,
        edges=True,
        fill_edge_geometry=True,
    )

    if roads.empty:
        raise RuntimeError("No road features were returned.")

    roads = roads.reset_index()
    roads = gpd.GeoDataFrame(
        roads,
        geometry="geometry",
        crs="EPSG:4326",
    )

    roads.to_file(
        ROADS_FILE,
        layer="bhopal_roads",
        driver="GPKG",
    )

    print("Road file saved:", ROADS_FILE)
    print("Road segments:", len(roads))
    print("Road CRS:", roads.crs)

    return roads


# --------------------------------------------------
# 6. DOWNLOAD HOSPITAL LOCATIONS
# --------------------------------------------------

def download_hospitals(boundary):
    polygon = boundary.geometry.union_all()

    hospitals = run_with_retries(
        "Downloading Bhopal hospitals",
        lambda: ox.features.features_from_polygon(
            polygon,
            tags={"amenity": "hospital"},
        ),
    )

    if hospitals.crs is None:
        raise RuntimeError("Hospital CRS is missing.")

    hospitals = hospitals.reset_index()
    hospitals = gpd.GeoDataFrame(
        hospitals,
        geometry="geometry",
        crs="EPSG:4326",
    )

    # Retain the OSM identifier and available attributes.
    hospitals.to_file(
        HOSPITALS_FILE,
        layer="bhopal_hospitals",
        driver="GPKG",
    )

    print("Hospital file saved:", HOSPITALS_FILE)
    print("Hospital features:", len(hospitals))
    print("Hospital CRS:", hospitals.crs)

    return hospitals


# --------------------------------------------------
# 7. MAIN WORKFLOW
# --------------------------------------------------

def main():
    summary = []

    try:
        # Download and save the study boundary.
        boundary = download_boundary()
        summary.append("Boundary download: SUCCESS")

        # Download roads separately.
        roads = download_roads(boundary)
        summary.append(f"Road segments: {len(roads)}")

        # Download hospitals separately.
        hospitals = download_hospitals(boundary)
        summary.append(f"Hospital features: {len(hospitals)}")

        summary.append("Overall status: SUCCESS")

        SUMMARY_FILE.write_text(
            "\n".join(summary) + "\n",
            encoding="utf-8",
        )

        print("\n" + "=" * 60)
        print("BHOPAL OSM DOWNLOAD COMPLETED")
        print("=" * 60)
        print("Road segments:", len(roads))
        print("Hospital features:", len(hospitals))
        print("Output folder:", OUTPUT_DIR)
        print("Summary:", SUMMARY_FILE)

    except Exception as exc:
        summary.append("Overall status: FAILED")
        summary.append(f"Error: {type(exc).__name__}: {exc}")

        SUMMARY_FILE.write_text(
            "\n".join(summary) + "\n",
            encoding="utf-8",
        )

        print("\nDOWNLOAD FAILED")
        print("Error:", exc)
        print("Check the error above before retrying.")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
