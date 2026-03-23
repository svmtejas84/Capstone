# Rasterising Demo (Bangalore 100 m Grid)

This folder contains a completed rasterisation demo for Bangalore using the local `bangalore.geojson` boundary.

## What Was Done

1. Loaded `bangalore.geojson` in EPSG:4326.
2. Reprojected geometry to EPSG:32643 (UTM Zone 43N) using GeoPandas.
3. Rasterised the polygon to a 100 m x 100 m grid using `rasterio.features.rasterize`.
4. Converted all raster cells inside the polygon back to vector polygon features.
5. Reprojected those grid features back to EPSG:4326 and saved as GeoJSON.
6. Plotted raster output with boundary overlay using Matplotlib.

## Command Used (from this folder)

```bash
cd /home/tejas/Downloads/Capstone/rasterising_demo
MPLBACKEND=Agg ../.venv/bin/python rasterize_grid.py
```

## Terminal Output Observed

```text
/home/tejas/Downloads/Capstone/rasterising_demo/rasterize_grid.py:115: UserWarning: FigureCanvasAgg is non-interactive, and thus cannot be shown
  plt.show()
Saved 107128 grid cells to: /home/tejas/Downloads/Capstone/rasterising_demo/bangalore_grid_100m.geojson
Saved plot to: /home/tejas/Downloads/Capstone/rasterising_demo/bangalore_grid_100m_plot.png
```

## Output Files

- `bangalore_grid_100m.geojson`: Grid polygons (inside cells only), stored in EPSG:4326.
- `bangalore_grid_100m_plot.png`: Raster visualisation with boundary overlay.
- `rasterize_grid.py`: Script used for the full workflow.

## Notes

- The `FigureCanvasAgg` warning is expected when running with `MPLBACKEND=Agg` (headless mode).
- Successful completion is indicated by the two `Saved ...` lines and generated output files.

## Methodology Decision (Square vs Hex)

For this project, **square-first is the recommended core methodology**.

### Why square-first is better here

1. The physics plane requirement is explicitly a live 100 m grid, which matches square raster cells directly.
2. Wind-plume advection and diffusion are cleaner to compute and cache on a fixed square raster.
3. The current ingestion -> plume -> routing stack already aligns with raster-style updates and avoids extra conversion steps.

### Where hexagons can still help

Hexagons are useful as a **secondary behavior layer** for isolation-focused entry/exit policy logic, because neighborhood symmetry can be better than square adjacency.

### Recommended hybrid strategy

1. Keep the 100 x 100 m square raster as the canonical computational plane.
2. Optionally compute hex-based control zones for localized isolation behavior.
3. Project hex decisions back to the square plane (for plume/routing updates) using overlap-based assignment.

This retains physical consistency and operational simplicity while allowing granular behavioral adjustments where needed.

## What "Policy" and "Behavior" Mean Here

In this project, plume physics and behavioral control are separate layers.

- Policy: static or slowly changing control rules.
  - Examples: protect vulnerable commuter zones, cap inflow in sensitive areas, enforce isolation preference during spikes.
- Behavior: time-varying operational state derived from policy plus live conditions.
  - Examples: entry pressure, exit pressure, temporary isolation penalty, reroute priority.

In practice:

1. Physics computes where pollution risk is.
2. Policy defines what the system wants to encourage or discourage.
3. Behavior becomes a real-time routing modifier.

## Exact Point Where Hex Overlay Enters

Hex should not replace the 100 m square plume plane. Hex should be inserted between plume output and route-cost finalization.

1. Run plume and concentration updates on the square raster (canonical layer).
2. Build or refresh a hex overlay from the latest square-state snapshot.
3. Compute hex behavioral scores (entry/exit ease, isolation penalty, vulnerability boost).
4. Project hex scores back onto square cells using overlap weights.
5. Compute final route cost using plume cost plus behavior cost.

Suggested formula:

```
C_final = C_plume + lambda * C_behavior
```

Where:

- `C_plume` is exposure cost from square-grid plume physics.
- `C_behavior` is overlap-weighted cost from the hex behavior overlay.
- `lambda` controls how strongly policy/behavior affects routing.

## Update justification
- Keeps physical modeling stable and aligned with the 100 m FR requirement.
- Preserves routing flexibility for granular entry/exit control.
- Avoids making the plume solver depend on hex geometry.
