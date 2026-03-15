# System Architecture

## Module Map

1. Live Environmental Component (GEE + Redis)
- Ingest Sentinel-5P NO2/SO2 as base toxicity.
- Pull ERA5/GFS wind and boundary layer height every 5-15 minutes.
- Inject traffic-based source spikes from API feeds.
- Project all variables into a 100m x 100m UTM raster grid.
- Push grid state to Redis Streams as the global truth.

2. PI-GNN Layer
- Build directed graph G=(V,E) from OSM.
- Sample raster toxicity to edges via bilinear interpolation.
- Apply angularly weighted diffusion using wind direction theta.
- Add urban canyon correction using building density.
- Produce dynamic edge concentrations Cedge for routing.

3. Equilibrium Matcher (Gale-Shapley)
- Side A: commuters ranked by distance and IDmin.
- Side B: route/segment bundles ranked by capacity and vulnerability fit.
- Return stable assignments to avoid herd behavior and preserve capacity.

4. Deployment Stack
- FastAPI orchestrator for ingestion, prediction, and routing APIs.
- Rust/WASM A* pathfinder for low-latency route scoring.
- Stake audit hashing for route provability.

## Primary Data Flow

1. Ingestion worker updates physics grid.
2. Grid snapshot event arrives in Redis stream.
3. PI-GNN service computes Cedge on active subgraph.
4. Matching service distributes users across candidate routes.
5. Routing service computes personalized path cost.
6. Audit service writes route hash and environmental seed.
