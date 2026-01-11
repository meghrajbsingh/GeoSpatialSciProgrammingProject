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
    """
    Pydantic model representing the cycling-friendliness metrics returned by the API.
    """
    pct_buildings_near_route: float
    avg_distance_to_route_m: float
    route_density_km_per_km2: float


@app.get("/metrics", response_model=CyclingMetrics)
def get_cycling_metrics(
    routes_fp: Optional[str] = None,
    buildings_fp: Optional[str] = None,
):
    """
    Calculate and return cycling-friendliness metrics for a study area.

    Query Parameters (optional):
        routes_fp: Path to the cycling routes GeoPackage file.
        buildings_fp: Path to the buildings GeoPackage file.

    Returns:
        CyclingMetrics: JSON object with:
            - pct_buildings_near_route: Percentage of buildings within 100m of a cycle route.
            - avg_distance_to_route_m: Average distance of buildings to nearest cycle route (meters).
            - route_density_km_per_km2: Cycling route density (km of route per km² of area).

    Notes:
        - Defaults to `data/enschede_road_network.gpkg` and `data/enschede_buildings.gpkg` if paths are not provided.
        - Raises FileNotFoundError if provided files do not exist.
    """
    # Determine default data directory
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

    # Load data and analyze
    routes, buildings = load_data(cycle_routes_fp, buildings_fp)
    result = analyze_study_area(routes, buildings)

    return result["metrics"]
