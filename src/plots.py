import matplotlib.pyplot as plt


def plot_building_proximity(buildings):
    fig, ax = plt.subplots(figsize=(10, 10))
    buildings.plot(
        column="nearest_route_m",
        cmap="viridis",
        legend=True,
        markersize=3,
        ax=ax,
    )
    ax.set_title("Distance to Nearest Cycling Route (m)")
    ax.axis("off")
    plt.show()


def plot_summary_bar(metrics):
    import pandas as pd

    pd.Series(metrics).plot(kind="bar", figsize=(8, 5))
    plt.title("Cycling-Friendliness Metrics")
    plt.ylabel("Value")
    plt.xticks(rotation=45, ha="right")
    plt.show()
