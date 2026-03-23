"""Rasterize Bangalore polygon into 100 m cells and export grid GeoJSON."""

from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from shapely.geometry import box


WGS84_CRS = "EPSG:4326"
UTM43N_CRS = "EPSG:32643"
CELL_SIZE_M = 100

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "bangalore.geojson"
OUTPUT_GRID_PATH = BASE_DIR / "bangalore_grid_100m.geojson"
OUTPUT_PLOT_PATH = BASE_DIR / "bangalore_grid_100m_plot.png"


def load_polygon_utm(path: Path) -> gpd.GeoDataFrame:
    """Load GeoJSON and return geometry in UTM zone 43N."""
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs(WGS84_CRS)
    else:
        gdf = gdf.to_crs(WGS84_CRS)
    return gdf.to_crs(UTM43N_CRS)


def build_grid_raster(gdf_utm: gpd.GeoDataFrame, cell_size_m: int):
    """Rasterize polygon to a fixed-size meter grid using from_bounds."""
    minx, miny, maxx, maxy = gdf_utm.total_bounds

    minx = np.floor(minx / cell_size_m) * cell_size_m
    miny = np.floor(miny / cell_size_m) * cell_size_m
    maxx = np.ceil(maxx / cell_size_m) * cell_size_m
    maxy = np.ceil(maxy / cell_size_m) * cell_size_m

    width = int((maxx - minx) / cell_size_m)
    height = int((maxy - miny) / cell_size_m)
    transform = from_bounds(minx, miny, maxx, maxy, width, height)

    raster = rasterize(
        [(geom, 1) for geom in gdf_utm.geometry if geom is not None],
        out_shape=(height, width),
        transform=transform,
        fill=0,
        dtype=np.uint8,
    )
    return raster, transform, (minx, miny, maxx, maxy)


def inside_cells_to_geojson(
    raster: np.ndarray,
    bounds: tuple[float, float, float, float],
    cell_size_m: int,
    output_path: Path,
) -> gpd.GeoDataFrame:
    """Convert inside raster cells to polygons, reproject to EPSG:4326, and save."""
    minx, miny, maxx, maxy = bounds
    rows, cols = raster.shape

    features = []
    for row in range(rows):
        for col in range(cols):
            if raster[row, col] != 1:
                continue

            cell_minx = minx + col * cell_size_m
            cell_maxx = cell_minx + cell_size_m
            cell_maxy = maxy - row * cell_size_m
            cell_miny = cell_maxy - cell_size_m

            features.append(
                {
                    "row": row,
                    "col": col,
                    "geometry": box(cell_minx, cell_miny, cell_maxx, cell_maxy),
                }
            )

    grid_utm = gpd.GeoDataFrame(features, geometry="geometry", crs=UTM43N_CRS)
    grid_wgs84 = grid_utm.to_crs(WGS84_CRS)
    grid_wgs84.to_file(output_path, driver="GeoJSON")
    return grid_wgs84


def plot_raster_with_boundary(
    raster: np.ndarray,
    bounds: tuple[float, float, float, float],
    gdf_utm: gpd.GeoDataFrame,
    output_path: Path,
) -> None:
    """Plot rasterized grid with polygon boundary overlay."""
    minx, miny, maxx, maxy = bounds

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(
        raster,
        extent=[minx, maxx, miny, maxy],
        origin="upper",
        cmap="viridis",
        interpolation="nearest",
    )
    gdf_utm.boundary.plot(ax=ax, color="white", linewidth=1.2)
    ax.set_title("Bangalore 100 m Raster Grid (EPSG:32643)")
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.show()


def main() -> None:
    gdf_utm = load_polygon_utm(INPUT_PATH)
    raster, transform, bounds = build_grid_raster(gdf_utm, CELL_SIZE_M)

    _ = transform  # transform is intentionally created via from_bounds per requirement.

    grid_wgs84 = inside_cells_to_geojson(
        raster=raster,
        bounds=bounds,
        cell_size_m=CELL_SIZE_M,
        output_path=OUTPUT_GRID_PATH,
    )
    plot_raster_with_boundary(
        raster=raster,
        bounds=bounds,
        gdf_utm=gdf_utm,
        output_path=OUTPUT_PLOT_PATH,
    )

    print(f"Saved {len(grid_wgs84)} grid cells to: {OUTPUT_GRID_PATH}")
    print(f"Saved plot to: {OUTPUT_PLOT_PATH}")


if __name__ == "__main__":
    main()
