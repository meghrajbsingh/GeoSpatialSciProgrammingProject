import geopandas as gpd
from pathlib import Path



data_path = Path(__file__).resolve().parents[2] / "data"
#original geojson file which is over 1 gb
input_path = data_path / "verkeerstypen.json"
#path for our output trimmed file for bicycle road network
output_path_gpkg  = data_path / "verkeerstypen_fiets.gpkg"
output_path_parq  = data_path / "verkeerstypen_fiets_only.parquet"


gdf = gpd.read_file(
    input_path
)


bike_allowed = (gdf["fiets_h"] == "J") | (gdf["fiets_t"] == "J")

#allowing mopeds and scooters but no other motorized vehicles
no_motor_traffic = (
    (gdf["auto_h"]    == "N") & (gdf["auto_t"]    == "N") &
    (gdf["mtrfts_h"]  == "N") & (gdf["mtrfts_t"]  == "N") &
    (gdf["autobs_h"]  == "N") & (gdf["autobs_t"]  == "N") &
    (gdf["vrchtt_h"]  == "N") & (gdf["vrchtt_t"]  == "N") &
    (gdf["lndbw_h"]   == "N") & (gdf["lndbw_t"]   == "N") &
    (gdf["aanhngr_h"] == "N") & (gdf["aanhngr_t"] == "N")
)


#segments where only bikes are allowed
gdf_bike_only = gdf[bike_allowed & no_motor_traffic]
#filter for only necessary columns
gdf_bike_only = gdf_bike_only[['id','geometry','fiets_h','fiets_t']]

print(len(gdf), "→", len(gdf_bike_only))


# Save trimmed dataset as geopackage
# gdf_bike_only.to_file(output_path_gpkg, driver="GPKG", layer="bike_only_paths")

#Save trimmed dataset as parquet
gdf_bike_only.to_parquet(output_path_parq)

