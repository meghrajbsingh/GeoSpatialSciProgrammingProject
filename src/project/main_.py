import geopandas as gpd
from pathlib import Path


# Load the geopackage
data_path = Path(__file__).resolve().parents[2] / "data" / "fietsnetwerken_vrij.gpkg"

gdf = gpd.read_file(data_path)

# See the first few rows
print(gdf.head())

# See all column names
print(gdf.columns)


# Check all unique regions
regions = gdf['regio'].unique()
print("Regions in dataset:", regions)

# get a count of how many road segments per region
region_counts = gdf['regio'].value_counts()
print(region_counts)