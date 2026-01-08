import geopandas as gpd
from project.io import load_data
from project.metrics import analyze_study_area, nearest_route_distance
from project.administrative import analyze_by_admin_region, join_metrics_to_regions
from src.plots import plot_building_proximity, plot_summary_bar


ROUTES_FP = "data/enschede_road_network.gpkg"
BUILDINGS_FP = "data/enschede_buildings.gpkg"
ADMIN_FP = "data/admin_regions.gpkg"


def main():
    routes, buildings = load_data(ROUTES_FP, BUILDINGS_FP)

    metrics = analyze_study_area(routes, buildings)
    print(metrics)

    buildings = nearest_route_distance(buildings, routes)
    plot_building_proximity(buildings)
    plot_summary_bar(metrics)

    #admin_gdf = gpd.read_file(ADMIN_FP).to_crs(epsg=28992)
    #results = analyze_by_admin_region(routes, buildings, admin_gdf)
    #admin_with_metrics = join_metrics_to_regions(admin_gdf, results)

    #print(admin_with_metrics.head())


if __name__ == "__main__":
    main()
