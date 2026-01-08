import geopandas as gpd


def load_data(cycle_route_fp, buildings_fp, target_crs=28992):
    routes = gpd.read_file(cycle_route_fp)
    buildings = gpd.read_file(buildings_fp)

    routes = routes[~routes.geometry.is_empty].to_crs(epsg=target_crs)
    buildings = buildings[~buildings.geometry.is_empty].to_crs(epsg=target_crs)

    return routes, buildings
