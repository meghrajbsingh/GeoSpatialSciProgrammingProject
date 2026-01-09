import geopandas as gpd
from shapely.geometry import LineString, Point

from project.cycle_friendly import (
    buffer_routes,
    buildings_near_routes,
    nearest_route_distance,
    route_density,
    analyze_study_area
)


def test_buffer_routes():
    test_line = gpd.GeoDataFrame(
        geometry=[LineString([(0, 0), (0, 10)])],
        crs="EPSG:28992"
    )
    buf = buffer_routes(test_line, distance_m=10)
    assert all(g.geom_type == "Polygon" for g in buf)


def test_buildings_near_routes_basic():
    buildings = gpd.GeoDataFrame(
        geometry=[Point(0, 0), Point(100, 100)],
        crs="EPSG:28992"
    )
    routes = gpd.GeoDataFrame(
        geometry=[LineString([(-10, 0), (10, 0)])],
        crs="EPSG:28992"
    )

    buffer = buffer_routes(routes, distance_m=20)
    pct = buildings_near_routes(buildings, buffer)

    assert abs(pct - 50.0) < 1e-6


def test_nearest_route_distance():
    buildings = gpd.GeoDataFrame(
        geometry=[Point(0, 0)],
        crs="EPSG:28992"
    )
    routes = gpd.GeoDataFrame(
        geometry=[LineString([(0, 10), (10, 10)])],
        crs="EPSG:28992"
    )

    result = nearest_route_distance(buildings, routes)
    assert abs(result["nearest_route_m"].iloc[0] - 10) < 1e-6


def test_route_density_simple_case():
    routes = gpd.GeoDataFrame(
        geometry=[LineString([(0, 0), (0, 1000)])],
        crs="EPSG:28992"
    )
    area_polygon = Point(0, 0).buffer(1000)

    density = route_density(routes, area_polygon)
    expected = 1 / (area_polygon.area / 1e6)

    assert abs(density - expected) < 1e-6


def test_analyze_study_area_outputs():
    routes = gpd.GeoDataFrame(
        geometry=[LineString([(0, 0), (0, 100)])],
        crs="EPSG:28992"
    )
    buildings = gpd.GeoDataFrame(
        geometry=[Point(10, 0), Point(200, 0)],
        crs="EPSG:28992"
    )

    metrics = analyze_study_area(routes, buildings)

    required_keys = {
        "pct_buildings_near_route",
        "avg_distance_to_route_m",
        "route_density_km_per_km2"
    }

    assert required_keys.issubset(metrics.keys())


def test_empty_buildings_handling():
    routes = gpd.GeoDataFrame(
        geometry=[LineString([(0, 0), (0, 100)])],
        crs="EPSG:28992"
    )
    buildings = gpd.GeoDataFrame(geometry=[], crs="EPSG:28992")

    metrics = analyze_study_area(routes, buildings)
    assert metrics["pct_buildings_near_route"] != metrics["pct_buildings_near_route"]  # NaN
