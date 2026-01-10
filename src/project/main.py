from project.cycle_friendly import load_data, analyze_study_area, plot_building_proximity, plot_summary_bar, plot_pairwise_density_vs_distance
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Script entry point
# --------------------------------------------------
def main():
    """
    Main script to load data, compute metrics, and generate plots.
    """
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
