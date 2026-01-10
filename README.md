<<<<<<< Updated upstream
# GeoSpatialSciProgrammingProject
Group Assignment for Sci Programming Course
=======
# GeoSpatial Bike Project

This project analyzes cycling-friendliness metrics in Enschede by evaluating the accessibility of buildings to cycling routes. It calculates metrics such as:

- Percentage of buildings near cycling routes
- Average distance of buildings to the nearest route
- Cycling route density in the study area

It also generates plots to visualize building proximity and summary metrics.

In the future we want to use this to compare metrics between different cities in the Netherlands.

## Installation

1. Install Poetry: https://python-poetry.org/docs/#installation
2. Clone the repository :

```bash
git clone https://github.com/meghrajbsingh/GeoSpatialSciProgrammingProject.git
cd GeoSpatialSciProgrammingProject
```

3. Install dependencies:

```bash
poetry install
```

## Running the code with poetry

1. Running analysis script :

```bash
poetry run python -m project.main
```

2. Running Tests :

```bash
poetry run pytest
```

Or pass custom paths to your data files:

```bash
poetry run python -m project.main --routes path/to/cycle_routes.gpkg --buildings path/to/buildings.gpkg
```

## Building the Package (.whl and .tar.gz)

To build a distributable package:

```bash
poetry build
```

This will generate files in the dist/ directory, e.g.:

```bash
dist/geospatialsciprogrammingproject-0.1.0-py3-none-any.whl
dist/geospatialsciprogrammingproject-0.1.0.tar.gz
```

## Installing the Wheel File

1. Activate your Python virtual environment (optional but recommended).
2. Install the .whl file using pip:

```bash
pip install path/to/geospatialsciprogrammingproject-0.1.0-py3-none-any.whl
```

## Running the Project From the Installed Wheel

After installation, run the project and provide file paths as arguments (optional — defaults will be used if no paths are provided):

```bash
python -m project.main --routes path/to/enschede_road_network.gpkg --buildings path/to/enschede_buildings.gpkg
```

Or with defaults:

```bash
python -m project.main
```

This will print the metrics and generate plots.


### Dependencies

The project dependencies are managed via Poetry and listed in pyproject.toml and poetry.lock. Key dependencies include:

geopandas

pandas

matplotlib

shapely

pyogrio

### Notes

Make sure the data/ folder exists in your project or current working directory and contains the required files:

enschede_road_network.gpkg

enschede_buildings.gpkg

All plots are generated using matplotlib.


## Running the REST API

The package provides a RESTful API to expose cycling-friendliness metrics via **FastAPI**.

### 1. Start the API

Activate your virtual environment and run:

```bash
uvicorn project.cycle_friendly:app --reload
```

The API runs at:

```bash
http://127.0.0.1:8000/docs
```

You can input the paths to your cycle routes and building files directly and execute to get JSON results.

You can also make a direct API call using /metrics endpoint which requires two parameters:
-routes_fp: Path to the cycling routes file
-buildings_fp: Path to the buildings file

### Notes
- Paths must exist and can be absolute or relative to the environment where the API runs
- The wheel does not include data files; you must provide your own
>>>>>>> Stashed changes
