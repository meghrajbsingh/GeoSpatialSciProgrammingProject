import geopandas as gpd
from shapely.geometry import LineString, Point
from project.metrics import (
    buffer_routes,
    buildings_near_routes,
    nearest_route_distance,
    route_density,
    analyze_study_area,
)


def test_buffer_routes():
    routes = gpd.GeoDataFrame(
        geometry=[LineString([(0, 0), (0, 10)])], crs="EPSG:28992"
    )
    buf = buffer_routes(routes, 10)
    assert all(g.geom_type == "Polygon" for g in buf)


def test_buildings_near_routes():
    buildings = gpd.GeoDataFrame(
        geometry=[Point(0, 0), Point(100, 100)], crs="EPSG:28992"
    )
    routes = gpd.GeoDataFrame(
        geometry=[LineString([(-10, 0), (10, 0)])], crs="EPSG:28992"
    )

    pct = buildings_near_routes(buildings, buffer_routes(routes, 20))
    assert abs(pct - 50.0) < 1e-6


def test_nearest_route_distance():
    buildings = gpd.GeoDataFrame(geometry=[Point(0, 0)], crs="EPSG:28992")
    routes = gpd.GeoDataFrame(
        geometry=[LineString([(0, 10), (10, 10)])], crs="EPSG:28992"
    )

    result = nearest_route_distance(buildings, routes)
    assert abs(result["nearest_route_m"].iloc[0] - 10) < 1e-6
