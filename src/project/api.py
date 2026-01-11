from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from pathlib import Path

from project.cycle_friendly import load_data, analyze_study_area

# --------------------------------------------------
# REST API (FastAPI) interface
# --------------------------------------------------


app = FastAPI(
    title="Cycling-Friendliness API",
    description="Expose cycling-friendliness metrics via REST",
    version="1.0.0",
)


class CyclingMetrics(BaseModel):
    pct_buildings_near_route: float
    avg_distance_to_route_m: float
    route_density_km_per_km2: float


@app.get("/metrics", response_model=CyclingMetrics)
def get_cycling_metrics(
    routes_fp: Optional[str] = None,
    buildings_fp: Optional[str] = None,
):
    BASE_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = BASE_DIR / "data"

    cycle_routes_fp = (
        Path(routes_fp)
        if routes_fp
        else DATA_DIR / "enschede_road_network.gpkg"
    )

    buildings_fp = (
        Path(buildings_fp)
        if buildings_fp
        else DATA_DIR / "enschede_buildings.gpkg"
    )

    if not cycle_routes_fp.exists():
        raise FileNotFoundError(f"Cycle routes file not found: {cycle_routes_fp}")
    if not buildings_fp.exists():
        raise FileNotFoundError(f"Buildings file not found: {buildings_fp}")

    routes, buildings = load_data(cycle_routes_fp, buildings_fp)
    result = analyze_study_area(routes, buildings)

    return result["metrics"]
