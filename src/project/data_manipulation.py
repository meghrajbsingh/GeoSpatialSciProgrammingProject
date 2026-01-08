from pathlib import Path
import geopandas as gpd
from typing import Iterable


# --- helper functions to create masks to filter our road networks geodataframe -------------------------------------------------------------

def bike_allowed(gdf: gpd.GeoDataFrame) -> gpd.Series:
    """Return mask for segments where bicycles are allowed in any direction."""
    return (gdf["fiets_h"] == "J") | (gdf["fiets_t"] == "J")


def no_motor_traffic(
    gdf: gpd.GeoDataFrame,
    motor_cols: Iterable[str]
) -> gpd.Series:
    """Return mask for segments without motorized traffic."""
    return (gdf[list(motor_cols)] == "N").all(axis=1)


# --- function to filter original gdf to return a new gdf where every row is a road that allows only bikes or scooters but no motor vehicles ----------------------------------------------------------

def filter_bike_only(
    gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """Filter GeoDataFrame to bicycle-only segments."""
    motor_columns = [
        "auto_h", "auto_t",
        "mtrfts_h", "mtrfts_t",
        "autobs_h", "autobs_t",
        "vrchtt_h", "vrchtt_t",
        "lndbw_h", "lndbw_t",
        "aanhngr_h", "aanhngr_t",
    ]

    mask = bike_allowed(gdf) & no_motor_traffic(gdf, motor_columns)

    return (
        gdf.loc[mask, ["id", "geometry", "fiets_h", "fiets_t"]]
        .reset_index(drop=True)
    )


# --- function to generate the lightweight parquet file from an input geoJSON road network file -------------------------------------------------------------

def geojson_to_bike_parquet(
    input_geojson: Path,
    output_parquet: Path
) -> None:
    """
    Read a GeoJSON file, extract bicycle-only segments,
    and write them to a Parquet file.
    """
    gdf = gpd.read_file(input_geojson)
    gdf_bike_only = filter_bike_only(gdf)

    print(f"{len(gdf)} → {len(gdf_bike_only)} bike-only segments")

    gdf_bike_only.to_parquet(output_parquet)


# --- here we can define paths for our input data and output parquet file for bike only road network (check documentation for download link for the geoJSON road network) -----------------------------------------------------------

if __name__ == "__main__":
    data_path = Path(__file__).resolve().parents[2] / "data"

    input_path = data_path / "verkeerstypen.json"
    output_path = data_path / "verkeerstypen_fiets_only.parquet"

    geojson_to_bike_parquet(input_path, output_path)
