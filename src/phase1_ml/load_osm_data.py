import os
import geopandas as gpd

from db_connection import get_engine


DATA_DIR = "data/shapefiles/osm/"

# Kolkata study area + 0.02 degree padding
CLIP_BBOX = (88.28, 22.43, 88.44, 22.69)


LAYERS_TO_LOAD = [
    ("gis_osm_roads_free_1.shp", "osm_roads"),
    ("gis_osm_buildings_a_free_1.shp", "osm_buildings"),
    ("gis_osm_landuse_a_free_1.shp", "osm_landuse"),
    ("gis_osm_pois_free_1.shp", "osm_poi"),
    ("gis_osm_pois_a_free_1.shp", "osm_poi_area"),
]


def load_layer(filename, table_name, engine):

    filepath = os.path.join(DATA_DIR, filename)

    print(f"Loading {filename} ...")

    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        return

    gdf = gpd.read_file(
        filepath,
        bbox=CLIP_BBOX
    )

    gdf = gdf.to_crs(epsg=4326)

    gdf.to_postgis(
        table_name,
        engine,
        if_exists="replace",
        index=False
    )

    print(
        f"  Loaded {len(gdf)} features "
        f"into table: {table_name}"
    )


def main():

    engine = get_engine()

    for filename, table_name in LAYERS_TO_LOAD:
        load_layer(
            filename,
            table_name,
            engine
        )

    print("All layers loaded successfully!")


if __name__ == "__main__":
    main()