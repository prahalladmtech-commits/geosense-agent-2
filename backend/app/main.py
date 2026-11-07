
import logging
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# --------------------------------------------------
# PROJECT PATH
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCORER_PATH = PROJECT_ROOT / "src" / "phase1_ml"
sys.path.insert(0, str(SCORER_PATH))

# --------------------------------------------------
# IMPORT EXISTING KOLKATA SCORING
# --------------------------------------------------

from site_scorer import score_location

# --------------------------------------------------
# IMPORT BHOPAL DRONE TERRAIN API
# --------------------------------------------------

from .services.bhopal_api import router as bhopal_router

# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("geosense")

# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="GeoSense Agent API",
    description="Geospatial site suitability and drone terrain analysis API",
    version="1.0.0"
)

# Register Bhopal API
app.include_router(bhopal_router)

# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://localhost:8082",
        "http://127.0.0.1:8082",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# --------------------------------------------------
# REQUEST MODEL - KOLKATA
# --------------------------------------------------

class LocationRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


# --------------------------------------------------
# KOLKATA DATA COVERAGE
# --------------------------------------------------

KOLKATA_BOUNDS = {
    "min_lat": 22.4303012,
    "max_lat": 22.6884943,
    "min_lon": 88.2796591,
    "max_lon": 88.4399995
}


# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "project": "GeoSense Agent",
        "status": "running",
        "version": "1.0.0",
        "study_areas": ["Kolkata", "Bhopal Drone Survey"]
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "GeoSense Backend",
        "database": "not checked",
        "model": "not checked"
    }


# --------------------------------------------------
# KOLKATA SITE SCORING ENDPOINT
# --------------------------------------------------

@app.post("/api/score-location")
def score_site(request: LocationRequest):

    lat = request.latitude
    lon = request.longitude

    # Prevent scoring outside Kolkata database coverage
    if not (
        KOLKATA_BOUNDS["min_lat"] <= lat <= KOLKATA_BOUNDS["max_lat"]
        and KOLKATA_BOUNDS["min_lon"] <= lon <= KOLKATA_BOUNDS["max_lon"]
    ):
        raise HTTPException(
            status_code=422,
            detail="Location is outside the available Kolkata dataset coverage."
        )

    try:
        result = score_location(lat, lon)

        return {
            "status": "success",
            "study_area": "Kolkata",
            "result": result
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except FileNotFoundError:
        logger.exception("Site scoring model file is missing")
        raise HTTPException(
            status_code=503,
            detail="The site scoring model is unavailable."
        )

    except Exception:
        logger.exception("Site scoring failed")
        raise HTTPException(
            status_code=500,
            detail="Site scoring failed. Check backend logs."
        )
