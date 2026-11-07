from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .bhopal_terrain import analyze_bhopal_location


router = APIRouter(prefix="/api/bhopal", tags=["Bhopal Drone Terrain"])


class BhopalLocationRequest(BaseModel):
    latitude: float = Field(ge=23.2539, le=23.2561)
    longitude: float = Field(ge=77.4563, le=77.4587)


@router.post("/terrain")
def bhopal_terrain(request: BhopalLocationRequest):
    try:
        result = analyze_bhopal_location(
            request.latitude,
            request.longitude
        )

        if result["nearest_ground_point_distance_m"] > 10:
            result["confidence_warning"] = (
                "Nearest ground point is more than 10 metres away. "
                "Treat this elevation as a rough estimate."
            )
        else:
            result["confidence_warning"] = None

        return {
            "status": "success",
            "study_area": "Bhopal Drone Survey",
            "result": result
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Bhopal drone point-cloud file is unavailable."
        )

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Bhopal terrain analysis failed."
        )