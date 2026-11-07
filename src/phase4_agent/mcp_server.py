
from pathlib import Path
import osmnx as ox

OUT_DIR = Path(r"C:\GeoSense_Agent\data\bhopal_osm")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ox.settings.log_console = True
ox.settings.timeout = 180

print("Downloading Bhopal boundary...")
boundary = ox.geocode_to_gdf("Bhopal, Madhya Pradesh, India")
boundary.to_file(
    OUT_DIR / "bhopal_boundary.gpkg",
    layer="boundary",
    driver="GPKG"
)
print("Boundary saved.")

print("Downloading Bhopal road network...")
graph = ox.graph_from_place(
    "Bhopal, Madhya Pradesh, India",
    network_type="drive"
)
nodes, roads = ox.graph_to_gdfs(graph)
roads = roads.reset_index()
roads.to_file(
    OUT_DIR / "bhopal_roads.gpkg",
    layer="roads",
    driver="GPKG"
)
print("Road features saved:", len(roads))

print("Downloading Bhopal hospitals...")
hospitals = ox.features_from_place(
    "Bhopal, Madhya Pradesh, India",
    tags={"amenity": "hospital"}
)

if not hospitals.empty:
    hospitals.to_file(
        OUT_DIR / "bhopal_hospitals.gpkg",
        layer="hospitals",
        driver="GPKG"
    )

print("Hospital features found:", len(hospitals))
print("Output directory:", OUT_DIR)
