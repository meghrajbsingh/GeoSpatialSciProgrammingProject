import geopandas as gpd
import math
from shapely.geometry import LineString, Point

from project.cycle_friendly import (
    buffer_routes,
    buildings_near_routes,
    nearest_route_distance,
    route_density,
    analyze_study_area
)


def test_buffer_routes():
    """Test that buffer_routes returns polygons around a line geometry."""
    test_line = gpd.GeoDataFrame(
        geometry=[LineString([(0, 0), (0, 10)])],
        crs="EPSG:28992"
    )
    buf = buffer_routes(test_line, distance_m=10)
    assert all(g.geom_type == "Polygon" for g in buf)


def test_buildings_near_routes_basic():
    """Test that buildings_near_routes calculates correct percentage of buildings near a route."""
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
    """Test that nearest_route_distance calculates the correct distance from buildings to routes."""
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
    """Test that route_density computes the expected density for a simple route and area."""
    routes = gpd.GeoDataFrame(
        geometry=[LineString([(0, 0), (0, 1000)])],
        crs="EPSG:28992"
    )
    area_polygon = Point(0, 0).buffer(1000)

    density = route_density(routes, area_polygon)
    expected = 1 / (area_polygon.area / 1e6)

    assert abs(density - expected) < 1e-6


def test_analyze_study_area_outputs():
    """Test that analyze_study_area returns all required metric keys in the result and also tests if it returns the buildings dataframe with nearest route column."""
    routes = gpd.GeoDataFrame(
        geometry=[LineString([(0, 0), (0, 100)])],
        crs="EPSG:28992"
    )
    buildings = gpd.GeoDataFrame(
        geometry=[Point(10, 0), Point(200, 0)],
        crs="EPSG:28992"
    )

    result = analyze_study_area(routes, buildings)

    # Check that metrics contain the required keys
    required_keys = {
        "pct_buildings_near_route",
        "avg_distance_to_route_m",
        "route_density_km_per_km2"
    }
    assert required_keys.issubset(result["metrics"].keys())

    # Check that building_points are returned
    building_points = result["building_points"]
    assert isinstance(building_points, gpd.GeoDataFrame)

    # Check that the 'nearest_route_m' column exists and has numeric values
    assert "nearest_route_m" in building_points.columns
    assert all(isinstance(val, (float, int)) for val in building_points["nearest_route_m"])



def test_empty_buildings_handling():
    """Test that analyze_study_area handles an empty buildings GeoDataFrame and returns NaN metrics."""
    routes = gpd.GeoDataFrame(
        geometry=[LineString([(0, 0), (0, 100)])],
        crs="EPSG:28992"
    )
    buildings = gpd.GeoDataFrame(geometry=[], crs="EPSG:28992")

    result = analyze_study_area(routes, buildings)
    metrics = result["metrics"]
    assert math.isnan(metrics["pct_buildings_near_route"])
    assert math.isnan(metrics["avg_distance_to_route_m"])
    assert math.isnan(metrics["route_density_km_per_km2"])
