import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point
from pathlib import Path

# --------------------------------------------------
# Data loading & preprocessing
# --------------------------------------------------
def load_data(cycle_route_fp, buildings_fp, target_crs=28992):
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
    return routes.geometry.buffer(distance_m)


def buildings_near_routes(building_points, routes_buffer):
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
    if building_points.empty:
        building_points["nearest_route_m"] = float("nan")
        return building_points

    routes_union = routes.geometry.unary_union
    building_points = building_points.copy()
    building_points["nearest_route_m"] = (
        building_points.geometry.distance(routes_union)
    )
    return building_points


def route_density(routes, area_polygon):
    total_length_km = routes.length.sum() / 1000
    area_km2 = area_polygon.area / 1e6
    return total_length_km / area_km2


def analyze_study_area(routes, building_points):
    buffer_100m = buffer_routes(routes, distance_m=100)
    pct_buildings_near = buildings_near_routes(building_points, buffer_100m)

    building_points = nearest_route_distance(building_points, routes)
    avg_distance = building_points["nearest_route_m"].mean()

    study_area = building_points.unary_union.convex_hull
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
    df = pd.DataFrame.from_dict(metrics, orient="index", columns=["Value"])
    df.plot(kind="bar", legend=False, figsize=(8, 5))
    plt.title("Cycling-Friendliness Metrics")
    plt.ylabel("Value")
    plt.xticks(rotation=45, ha="right")
    plt.show()


# --------------------------------------------------
# Script entry point
# --------------------------------------------------
def main():
    BASE_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = BASE_DIR / "data"

    cycle_routes_fp = DATA_DIR / "enschede_road_network.gpkg"
    buildings_fp = DATA_DIR / "enschede_buildings.gpkg"

    routes, buildings = load_data(cycle_routes_fp, buildings_fp)
    building_points = buildings

    result = analyze_study_area(routes, building_points)

    metrics = result["metrics"]
    building_points = result["building_points"]

    print(pd.Series(metrics))

    plot_building_proximity(building_points)
    plot_summary_bar(metrics)
    plot_pairwise_density_vs_distance(metrics)


if __name__ == "__main__":
    main()
