import geopandas as gpd
import pandas as pd
from .metrics import buffer_routes, buildings_near_routes, nearest_route_distance


def analyze_by_admin_region(routes, building_points, admin_gdf, buffer_dist=100):
    results = []

    for _, region in admin_gdf.iterrows():
        geom = region.geometry

        region_routes = gpd.clip(routes, geom)
        region_buildings = building_points[building_points.within(geom)]

        if region_routes.empty or region_buildings.empty:
            continue

        pct_near = buildings_near_routes(
            region_buildings, buffer_routes(region_routes, buffer_dist)
        )

        region_buildings = nearest_route_distance(region_buildings, region_routes)
        avg_dist = region_buildings["nearest_route_m"].mean()

        length_km = region_routes.length.sum() / 1000
        area_km2 = geom.area / 1e6
        density = length_km / area_km2

        results.append(
            {
                "region_name": region["name"],
                "pct_buildings_near_route": pct_near,
                "avg_distance_to_route_m": avg_dist,
                "route_density_km_per_km2": density,
            }
        )

    return pd.DataFrame(results)


def join_metrics_to_regions(admin_gdf, results_df):
    return admin_gdf.merge(
        results_df, left_on="name", right_on="region_name", how="left"
    )
