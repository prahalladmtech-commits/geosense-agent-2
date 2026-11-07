
import logging
import os
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCORER_PATH = PROJECT_ROOT / "src" / "phase1_ml"

if str(SCORER_PATH) not in sys.path:
    sys.path.insert(0, str(SCORER_PATH))

# ============================================================
# EXISTING KOLKATA ML SCORING
# ============================================================

from site_scorer import score_location

# ============================================================
# BHOPAL DRONE TERRAIN API
# ============================================================

from .services.bhopal_api import router as bhopal_router

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("geosense")

# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="GeoSense Agent API",
    description=(
        "Geospatial site suitability, "
        "Kolkata ML analysis and Bhopal drone terrain analysis."
    ),
    version="1.1.0"
)

# ============================================================
# CORS CONFIGURATION
# ============================================================

DEFAULT_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:8082",
    "http://127.0.0.1:8082",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://prahalladmtech-commits.github.io",
]

configured_origins = os.getenv("GEOSENSE_CORS_ORIGINS", "")

if configured_origins.strip():
    ALLOWED_ORIGINS = [
        origin.strip().rstrip("/")
        for origin in configured_origins.split(",")
        if origin.strip()
    ]
else:
    ALLOWED_ORIGINS = DEFAULT_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ============================================================
# REGISTER BHOPAL API
# ============================================================

app.include_router(bhopal_router)

# ============================================================
# REQUEST MODEL - KOLKATA
# ============================================================

class LocationRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

# ============================================================
# KOLKATA DATA COVERAGE
# ============================================================

KOLKATA_BOUNDS = {
    "min_lat": 22.4303012,
    "max_lat": 22.6884943,
    "min_lon": 88.2796591,
    "max_lon": 88.4399995,
}

# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "project": "GeoSense Agent",
        "status": "running",
        "version": "1.1.0",
        "study_areas": [
            "Kolkata",
            "Bhopal Drone Survey"
        ],
    }

# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "GeoSense Backend",
        "database": "not checked",
        "model": "not checked",
    }

# ============================================================
# KOLKATA SITE SCORING ENDPOINT
# ============================================================

@app.post("/api/score-location")
def score_site(request: LocationRequest):

    latitude = request.latitude
    longitude = request.longitude

    # Validate Kolkata dataset coverage
    inside_coverage = (
        KOLKATA_BOUNDS["min_lat"]
        <= latitude
        <= KOLKATA_BOUNDS["max_lat"]
        and
        KOLKATA_BOUNDS["min_lon"]
        <= longitude
        <= KOLKATA_BOUNDS["max_lon"]
    )

    if not inside_coverage:
        raise HTTPException(
            status_code=422,
            detail=(
                "Location is outside the available "
                "Kolkata dataset coverage."
            ),
        )

    try:
        result = score_location(latitude, longitude)

        return {
            "status": "success",
            "study_area": "Kolkata",
            "result": result,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except FileNotFoundError:
        logger.exception("Site scoring model file is missing")

        raise HTTPException(
            status_code=503,
            detail="The site scoring model is unavailable.",
        )

    except Exception:
        logger.exception("Kolkata site scoring failed")

        raise HTTPException(
            status_code=500,
            detail="Site scoring failed. Check backend logs.",
        )
