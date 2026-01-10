import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point
from pathlib import Path

# --------------------------------------------------
# Data loading & preprocessing
# --------------------------------------------------
def load_data(cycle_route_fp, buildings_fp, target_crs=28992):
    """
    Load cycle route and building data from files, remove empty geometries,
    and reproject to the target CRS (default EPSG:28992).
    
    Args:
        cycle_route_fp (str or Path): File path to cycle routes.
        buildings_fp (str or Path): File path to buildings.
        target_crs (int): EPSG code to reproject geometries.
    
    Returns:
        tuple[GeoDataFrame, GeoDataFrame]: routes and buildings GeoDataFrames.
    """
    routes = gpd.read_file(cycle_route_fp)
    buildings = gpd.read_file(buildings_fp)

    routes = routes[~routes.geometry.is_empty]
    buildings = buildings[~buildings.geometry.is_empty]

    routes = routes.to_crs(epsg=target_crs)
    buildings = buildings.to_crs(epsg=target_crs)

    return routes, buildings


# --------------------------------------------------
# Core analysis functions
# --------------------------------------------------
def buffer_routes(routes, distance_m=100):
    """
    Create a buffer polygon around each route.

    Args:
        routes (GeoDataFrame): Line geometries representing routes.
        distance_m (float): Buffer distance in meters.

    Returns:
        GeoSeries: Buffered polygons around routes.
    """
    return routes.geometry.buffer(distance_m)


def buildings_near_routes(building_points, routes_buffer):
    """
    Compute the percentage of buildings located within route buffers.

    Args:
        building_points (GeoDataFrame): Point geometries of buildings.
        routes_buffer (GeoSeries): Buffered polygons of routes.

    Returns:
        float: Percentage of buildings near routes, or NaN if no buildings.
    """
    if building_points.empty:
        return float("nan")

    buffer_gdf = gpd.GeoDataFrame(
        geometry=routes_buffer,
        crs=building_points.crs
    )

    joined = gpd.sjoin(
        building_points,
        buffer_gdf,
        how="inner",
        predicate="intersects"
    )

    near_count = joined.shape[0]
    total_count = building_points.shape[0]

    return (near_count / total_count) * 100


def nearest_route_distance(building_points, routes):
    """
    Compute distance from each building to the nearest route.

    Args:
        building_points (GeoDataFrame): Point geometries of buildings.
        routes (GeoDataFrame): Line geometries of routes.

    Returns:
        GeoDataFrame: Buildings with a new column 'nearest_route_m'.
    """
    if building_points.empty:
        building_points["nearest_route_m"] = float("nan")
        return building_points

    routes_union = routes.geometry.union_all()
    building_points = building_points.copy()
    building_points["nearest_route_m"] = (
        building_points.geometry.distance(routes_union)
    )
    return building_points


def route_density(routes, area_polygon):
    """
    Compute cycling route density as total route length per unit area.

    Args:
        routes (GeoDataFrame): Line geometries of routes.
        area_polygon (shapely Polygon): Polygon defining the study area.

    Returns:
        float: Route density in km per km², or NaN if area is empty.
    """
    if area_polygon.is_empty or area_polygon.area == 0:
        return float("nan")
    total_length_km = routes.length.sum() / 1000
    area_km2 = area_polygon.area / 1e6
    return total_length_km / area_km2


def analyze_study_area(routes, building_points):
    """
    Analyze the study area for cycling-friendliness metrics.

    Computes:
      - Percentage of buildings near routes
      - Average distance of buildings to nearest route
      - Route density in the study area

    Args:
        routes (GeoDataFrame): Line geometries of cycling routes.
        building_points (GeoDataFrame): Point geometries of buildings.

    Returns:
        dict: 
            - 'metrics': dictionary with computed metrics
            - 'building_points': GeoDataFrame with nearest route distances
    """
    buffer_100m = buffer_routes(routes, distance_m=100)
    pct_buildings_near = buildings_near_routes(building_points, buffer_100m)

    building_points = nearest_route_distance(building_points, routes)
    avg_distance = building_points["nearest_route_m"].mean()

    study_area = building_points.union_all().convex_hull
    density = route_density(routes, study_area)

    return {
        "metrics": {
            "pct_buildings_near_route": pct_buildings_near,
            "avg_distance_to_route_m": avg_distance,
            "route_density_km_per_km2": density
        },
        "building_points": building_points
    }


# --------------------------------------------------
# Plotting utilities
# --------------------------------------------------
def plot_building_proximity(building_points):
    """
    Plot building locations colored by distance to nearest route.

    Args:
        building_points (GeoDataFrame): Must include 'nearest_route_m' column.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    building_points.plot(
        column="nearest_route_m",
        cmap="viridis",
        legend=True,
        markersize=3,
        ax=ax
    )
    ax.set_title("Distance of Buildings to Nearest Cycling Route (m)")
    ax.axis("off")
    plt.show()


def plot_pairwise_density_vs_distance(metrics):
    """
    Scatter plot of route density vs average building distance.

    Args:
        metrics (dict): Dictionary containing 'route_density_km_per_km2' 
                        and 'avg_distance_to_route_m'.
    """
    plt.figure(figsize=(6, 6))
    plt.scatter(
        metrics["route_density_km_per_km2"],
        metrics["avg_distance_to_route_m"]
    )
    plt.xlabel("Cycling Route Density (km / km²)")
    plt.ylabel("Average Distance to Nearest Route (m)")
    plt.title("Route Density vs. Accessibility")
    plt.grid(True)
    plt.show()


def plot_summary_bar(metrics):
    """
    Plot a bar chart summarizing cycling-friendliness metrics.

    Args:
        metrics (dict): Dictionary of metrics to plot.
    """
    df = pd.DataFrame.from_dict(metrics, orient="index", columns=["Value"])
    df.plot(kind="bar", legend=False, figsize=(8, 5))
    plt.title("Cycling-Friendliness Metrics")
    plt.ylabel("Value")
    plt.xticks(rotation=45, ha="right")
    plt.show()

# --------------------------------------------------
# REST API (FastAPI) interface
# --------------------------------------------------

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

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
    """
    Return cycling-friendliness metrics as JSON.

    Query parameters (optional):
        routes_fp: Path to cycling routes file
        buildings_fp: Path to buildings file

    If not provided, defaults to data/enschede_*.gpkg
    """

    # Reproduce CLI default behavior
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

    # Load + analyze (reuse existing logic)
    routes, buildings = load_data(cycle_routes_fp, buildings_fp)
    result = analyze_study_area(routes, buildings)

    return result["metrics"]