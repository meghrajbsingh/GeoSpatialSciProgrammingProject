import geopandas as gpd
import numpy as np


def buffer_routes(routes, distance_m=100):
    return routes.geometry.buffer(distance_m)


def buildings_near_routes(building_points, routes_buffer):
    if building_points.empty:
        return np.nan

    buffer_gdf = gpd.GeoDataFrame(geometry=routes_buffer, crs=building_points.crs)

    joined = gpd.sjoin(
        building_points,
        buffer_gdf,
        how="inner",
        predicate="intersects",
    )

    return (len(joined) / len(building_points)) * 100


def nearest_route_distance(building_points, routes):
    if building_points.empty:
        building_points = building_points.copy()
        building_points["nearest_route_m"] = np.nan
        return building_points

    routes_union = routes.geometry.unary_union
    building_points = building_points.copy()
    building_points["nearest_route_m"] = building_points.geometry.distance(routes_union)
    return building_points


def route_density(routes, area_polygon):
    if area_polygon.is_empty or area_polygon.area == 0:
        return np.nan

    total_length_km = routes.length.sum() / 1000
    area_km2 = area_polygon.area / 1e6
    return total_length_km / area_km2


def analyze_study_area(routes, building_points):
    buffer_100m = buffer_routes(routes, 100)
    pct_near = buildings_near_routes(building_points, buffer_100m)

    buildings_with_dist = nearest_route_distance(building_points, routes)
    avg_distance = buildings_with_dist["nearest_route_m"].mean()

    study_area = building_points.unary_union.convex_hull
    density = route_density(routes, study_area)

    return {
        "pct_buildings_near_route": pct_near,
        "avg_distance_to_route_m": avg_distance,
        "route_density_km_per_km2": density,
    }
