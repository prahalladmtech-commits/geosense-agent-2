
# ============================================================
# GeoSense Agent — Phase 1
# Site Suitability Scoring for Kolkata
# Windows and Docker compatible
# ============================================================

import os
from pathlib import Path

import joblib
import pandas as pd
import geopandas as gpd
import shap

from shapely.geometry import Point
from db_connection import get_engine


# ============================================================
# CONFIGURATION
# ============================================================

# Automatically detect project root.
# Windows: C:\GeoSense_Agent
# Docker:  /app (when project is copied to /app)

PROJECT_DIR = Path(__file__).resolve().parents[2]

# Kolkata UTM Zone 45N
# Used for accurate distance calculations in metres.
METRIC_CRS = 32645

# These MUST match the features used to train the model.
FEATURE_NAMES = [
    "dist_road_m",
    "dist_hospital_m",
    "flood_risk"
]

# Trained model location.
MODEL_FILE = (
    PROJECT_DIR
    / "models"
    / "saved"
    / "site_scorer_model.pkl"
)


# ============================================================
# MODEL CACHE
# ============================================================

_model = None
_explainer = None


def _load_model():
    """
    Load the trained classification model
    and create its SHAP explainer.
    """

    global _model, _explainer

    if _model is None:

        if not MODEL_FILE.is_file():
            raise FileNotFoundError(
                f"Model file not found:\n{MODEL_FILE}"
            )

        _model = joblib.load(MODEL_FILE)

        _explainer = shap.TreeExplainer(_model)

    return _model, _explainer


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def _get_features_for_point(lat, lon, engine):
    """
    Calculate geographic features for a given
    latitude and longitude.

    Features:
        - Distance to nearest road
        - Distance to nearest hospital
        - Flood risk
    """

    # --------------------------------------------------------
    # Create input point in WGS84
    # --------------------------------------------------------

    point = Point(float(lon), float(lat))

    point_gdf = gpd.GeoDataFrame(
        [{"geometry": point}],
        crs="EPSG:4326"
    )

    # --------------------------------------------------------
    # Re-project input point to metric CRS
    # --------------------------------------------------------

    point_proj = point_gdf.to_crs(
        epsg=METRIC_CRS
    )

    point_geometry = point_proj.geometry.iloc[0]

    # ========================================================
    # DISTANCE TO NEAREST ROAD
    # ========================================================

    roads = gpd.read_postgis(
        """
        SELECT geometry
        FROM osm_roads
        """,
        engine,
        geom_col="geometry"
    )

    if roads.empty:
        raise ValueError(
            "No road geometries found in osm_roads."
        )

    roads_proj = roads.to_crs(
        epsg=METRIC_CRS
    )

    dist_road = roads_proj.geometry.distance(
        point_geometry
    ).min()

    # ========================================================
    # HOSPITALS — POINT FEATURES
    # ========================================================

    hospitals_point = gpd.read_postgis(
        """
        SELECT geometry
        FROM osm_poi
        WHERE fclass = 'hospital'
        """,
        engine,
        geom_col="geometry"
    )

    # ========================================================
    # HOSPITALS — AREA FEATURES
    # ========================================================

    hospitals_area = gpd.read_postgis(
        """
        SELECT geometry
        FROM osm_poi_area
        WHERE fclass = 'hospital'
        """,
        engine,
        geom_col="geometry"
    )

    # --------------------------------------------------------
    # Project hospital polygons FIRST.
    # Then calculate centroids.
    # --------------------------------------------------------

    if not hospitals_area.empty:

        hospitals_area = hospitals_area.to_crs(
            epsg=METRIC_CRS
        )

        hospitals_area = hospitals_area.copy()

        hospitals_area["geometry"] = (
            hospitals_area.geometry.centroid
        )

    # --------------------------------------------------------
    # Project point hospitals to metric CRS
    # --------------------------------------------------------

    if not hospitals_point.empty:

        hospitals_point = hospitals_point.to_crs(
            epsg=METRIC_CRS
        )

    # ========================================================
    # COMBINE HOSPITAL DATA
    # ========================================================

    hospital_frames = []

    if not hospitals_point.empty:
        hospital_frames.append(
            hospitals_point
        )

    if not hospitals_area.empty:
        hospital_frames.append(
            hospitals_area
        )

    if hospital_frames:

        hospitals = gpd.GeoDataFrame(
            pd.concat(
                hospital_frames,
                ignore_index=True
            ),
            crs=f"EPSG:{METRIC_CRS}"
        )

        # All hospital geometries are already
        # in the metric CRS.
        hospitals_proj = hospitals

        dist_hospital = hospitals_proj.geometry.distance(
            point_geometry
        ).min()

    else:

        dist_hospital = float("inf")

    # ========================================================
    # FLOOD RISK
    # ========================================================

    # No flood_zones table is currently available
    # in the Phase 1 Kolkata dataset.
    #
    # Therefore flood risk remains the documented
    # placeholder value.

    flood_risk = 0.0

    # ========================================================
    # RETURN FEATURES
    # ========================================================

    return {
        "dist_road_m": float(dist_road),
        "dist_hospital_m": float(dist_hospital),
        "flood_risk": float(flood_risk)
    }


# ============================================================
# SITE SCORING FUNCTION
# ============================================================

def score_location(lat: float, lon: float) -> dict:
    """
    Score a geographic location.

    Parameters
    ----------
    lat : float
        Latitude of the location.

    lon : float
        Longitude of the location.

    Returns
    -------
    dict
        Contains:
            latitude
            longitude
            opportunity_score
            risk_score
            features
            shap_explanation
            verdict
    """

    # --------------------------------------------------------
    # Validate coordinates
    # --------------------------------------------------------

    lat = float(lat)
    lon = float(lon)

    if not (-90 <= lat <= 90):
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if not (-180 <= lon <= 180):
        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    # --------------------------------------------------------
    # Database connection
    # --------------------------------------------------------

    engine = get_engine()

    # --------------------------------------------------------
    # Load trained model
    # --------------------------------------------------------

    model, explainer = _load_model()

    # --------------------------------------------------------
    # Calculate geographic features
    # --------------------------------------------------------

    features = _get_features_for_point(
        lat,
        lon,
        engine
    )

    # ========================================================
    # CREATE MODEL INPUT
    # ========================================================

    # Use DataFrame with the exact feature names
    # used during model training.

    X = pd.DataFrame(
        [[
            features["dist_road_m"],
            features["dist_hospital_m"],
            features["flood_risk"]
        ]],
        columns=FEATURE_NAMES
    )

    # ========================================================
    # MODEL PREDICTION
    # ========================================================

    probabilities = model.predict_proba(X)[0]

    # Probability of class 0 = poor site
    poor_probability = float(probabilities[0])

    # Probability of class 1 = good site
    good_probability = float(probabilities[1])

    # --------------------------------------------------------
    # Convert probability to 0–10 scores
    # --------------------------------------------------------

    opportunity_score = round(
        good_probability * 10,
        2
    )

    risk_score = round(
        poor_probability * 10,
        2
    )

    # ========================================================
    # SHAP EXPLANATION
    # ========================================================

    shap_values = explainer.shap_values(X)

    # --------------------------------------------------------
    # SHAP output differs between versions/models.
    # Handle common formats safely.
    # --------------------------------------------------------

    if isinstance(shap_values, list):

        # Binary classifier:
        # class 1 = GOOD SITE
        shap_positive = shap_values[1][0]

    elif getattr(shap_values, "ndim", 0) == 3:

        # Shape:
        # samples × features × classes
        shap_positive = shap_values[0, :, 1]

    else:

        # Standard 2D output
        shap_positive = shap_values[0]

    shap_explanation = {
        feature: round(
            float(value),
            4
        )
        for feature, value in zip(
            FEATURE_NAMES,
            shap_positive
        )
    }

    # ========================================================
    # VERDICT
    # ========================================================

    if opportunity_score > 5:

        verdict = "GOOD SITE"

    else:

        verdict = "POOR SITE"

    # ========================================================
    # FINAL RESULT
    # ========================================================

    result = {
        "latitude": lat,
        "longitude": lon,
        "opportunity_score": opportunity_score,
        "risk_score": risk_score,
        "features": features,
        "shap_explanation": shap_explanation,
        "verdict": verdict
    }

    return result


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    # Example Kolkata location
    test_latitude = 22.5535
    test_longitude = 88.3520

    result = score_location(
        test_latitude,
        test_longitude
    )

    print()
    print("GeoSense Site Score")
    print("=" * 50)

    print(
        f"latitude            : "
        f"{result['latitude']}"
    )

    print(
        f"longitude           : "
        f"{result['longitude']}"
    )

    print(
        f"opportunity_score   : "
        f"{result['opportunity_score']}"
    )

    print(
        f"risk_score          : "
        f"{result['risk_score']}"
    )

    print(
        f"features            : "
        f"{result['features']}"
    )

    print(
        f"shap_explanation    : "
        f"{result['shap_explanation']}"
    )

    print(
        f"verdict             : "
        f"{result['verdict']}"
    )

    print()
