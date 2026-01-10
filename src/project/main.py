import argparse
from pathlib import Path
import pandas as pd
from project.cycle_friendly import (
    load_data,
    analyze_study_area,
    plot_building_proximity,
    plot_summary_bar,
    plot_pairwise_density_vs_distance
)

def parse_arguments():
    """
    Parse command-line arguments for input file paths.

    Returns:
        argparse.Namespace: Attributes:
            - routes (str or None): Path to the cycle routes file.
            - buildings (str or None): Path to the buildings file.
    """
    parser = argparse.ArgumentParser(
        description="Analyze cycling-friendliness metrics for a study area."
    )
    parser.add_argument(
        "--routes",
        type=str,
        default=None,
        help="Path to the cycle routes file (GeoPackage or similar)."
    )
    parser.add_argument(
        "--buildings",
        type=str,
        default=None,
        help="Path to the buildings file (GeoPackage or similar)."
    )
    return parser.parse_args()


def main():
    """
    Main function to load data, compute cycling-friendliness metrics,
    and generate plots.

    Behavior:
        - If run from the repo without arguments, defaults to `data/enschede_*.gpkg`.
        - If paths are provided via command-line arguments, uses them.
        - Validates that the files exist before proceeding.
    """
    args = parse_arguments()

    # Determine default data directory (two levels up from main.py)
    BASE_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = BASE_DIR / "data"

    # Determine cycle routes file path
    if args.routes:
        cycle_routes_fp = Path(args.routes)
    else:
        cycle_routes_fp = DATA_DIR / "enschede_road_network.gpkg"

    # Determine buildings file path
    if args.buildings:
        buildings_fp = Path(args.buildings)
    else:
        buildings_fp = DATA_DIR / "enschede_buildings.gpkg"

    # Check if files exist
    if not cycle_routes_fp.exists():
        raise FileNotFoundError(f"Cycle routes file not found: {cycle_routes_fp}")
    if not buildings_fp.exists():
        raise FileNotFoundError(f"Buildings file not found: {buildings_fp}")

    # Print paths for debugging
    print(f"Using cycle routes file: {cycle_routes_fp}")
    print(f"Using buildings file: {buildings_fp}")

    # Load data
    routes, buildings = load_data(cycle_routes_fp, buildings_fp)
    building_points = buildings

    # Analyze study area
    result = analyze_study_area(routes, building_points)
    metrics = result["metrics"]
    building_points = result["building_points"]

    # Print metrics
    print("\nCycling-Friendliness Metrics:")
    print(pd.Series(metrics))

    # Generate plots
    plot_building_proximity(building_points)
    plot_summary_bar(metrics)
    plot_pairwise_density_vs_distance(metrics)


if __name__ == "__main__":
    main()
