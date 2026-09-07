import geopandas as gpd
import pandas as pd
import numpy as np

from db_connection import get_engine


# Kolkata distance calculations
# WGS 84 / UTM Zone 45N
METRIC_CRS = 32645


def load_layer(sql, engine):
    """Read a PostGIS layer into a GeoDataFrame."""

    return gpd.read_postgis(
        sql,
        engine,
        geom_col="geometry"
    )


def calc_distance_to_nearest(
    candidates_gdf,
    layer_gdf
):
    """
    Calculate distance from every candidate
    to the nearest feature in metres.
    """

    candidates_proj = candidates_gdf.to_crs(
        epsg=METRIC_CRS
    )

    layer_proj = layer_gdf.to_crs(
        epsg=METRIC_CRS
    )

    distances = candidates_proj.geometry.apply(
        lambda point:
        layer_proj.geometry.distance(point).min()
    )

    return distances


def load_hospitals(engine):
    """
    Load hospitals from both OSM POI tables.

    Point hospitals are used directly.
    Area hospitals are converted to centroids
    after projection to the metric CRS.
    """

    # Hospital points
    points = load_layer(
        """
        SELECT geometry
        FROM osm_poi
        WHERE fclass = 'hospital'
        """,
        engine
    )

    # Hospital polygons/areas
    areas = load_layer(
        """
        SELECT geometry
        FROM osm_poi_area
        WHERE fclass = 'hospital'
        """,
        engine
    )

    print(
        f"Hospital points found: {len(points)}"
    )

    print(
        f"Hospital areas found: {len(areas)}"
    )

    # Convert area hospitals to centroids
    areas = areas.to_crs(
        epsg=METRIC_CRS
    )

    areas["geometry"] = areas.geometry.centroid

    # Return to WGS84
    areas = areas.to_crs(
        epsg=4326
    )

    # Combine point + area hospitals
    hospitals = pd.concat(
        [points, areas],
        ignore_index=True
    )

    hospitals = gpd.GeoDataFrame(
        hospitals,
        geometry="geometry",
        crs="EPSG:4326"
    )

    print(
        f"Total hospitals: {len(hospitals)}"
    )

    return hospitals


def assign_flood_risk(
    candidates_gdf,
    engine
):
    """
    Assign flood-risk score.

    If flood_zones exists, use:
        high   = 8
        medium = 5
        low    = 2

    Otherwise use 0 as an explicit placeholder.
    """

    try:

        flood = load_layer(
            """
            SELECT geometry, risk_level
            FROM flood_zones
            """,
            engine
        )

        joined = gpd.sjoin(
            candidates_gdf,
            flood,
            how="left",
            predicate="within"
        )

        risk_map = {
            "high": 8,
            "medium": 5,
            "low": 2
        }

        return (
            joined["risk_level"]
            .map(risk_map)
            .fillna(0)
        )

    except Exception:

        print(
            "flood_zones table not found - "
            "flood_risk set to 0 (placeholder)"
        )

        return pd.Series(
            np.zeros(len(candidates_gdf))
        )


def build_feature_table(
    candidates_gdf,
    engine
):

    # Basic candidate information
    df = candidates_gdf[
        [
            "location_id",
            "latitude",
            "longitude"
        ]
    ].copy()

    # -------------------------------------------------
    # ROAD DISTANCE
    # -------------------------------------------------

    print(
        "Calculating: distance to nearest road ..."
    )

    roads = load_layer(
        """
        SELECT geometry
        FROM osm_roads
        """,
        engine
    )

    df["dist_road_m"] = calc_distance_to_nearest(
        candidates_gdf,
        roads
    )

    # -------------------------------------------------
    # HOSPITAL DISTANCE
    # -------------------------------------------------

    print(
        "Calculating: distance to nearest hospital ..."
    )

    hospitals = load_hospitals(engine)

    df["dist_hospital_m"] = calc_distance_to_nearest(
        candidates_gdf,
        hospitals
    )

    # -------------------------------------------------
    # FLOOD RISK
    # -------------------------------------------------

    print(
        "Calculating: flood risk score ..."
    )

    df["flood_risk"] = assign_flood_risk(
        candidates_gdf,
        engine
    )

    print(
        "Feature table built with",
        len(df),
        "locations and",
        len(df.columns),
        "columns"
    )

    return df


if __name__ == "__main__":

    print("Connecting to PostGIS...")

    engine = get_engine()

    print("Reading candidate locations...")

    candidates = gpd.read_file(
        "data/processed/candidate_locations.shp"
    )

    # Shapefile truncates location_id
    candidates = candidates.rename(
        columns={
            "location_i": "location_id"
        }
    )

    print(
        f"Candidate locations: {len(candidates)}"
    )

    features = build_feature_table(
        candidates,
        engine
    )

    features.to_csv(
        "data/processed/features.csv",
        index=False
    )

    print(
        "Features saved to "
        "data/processed/features.csv"
    )