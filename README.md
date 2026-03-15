# Urban Toxicity Orchestrator (Capstone)

A cross-scale geospatial logic for real-time urban toxicity orchestration to aid healthy navigation for vulnerable commuters.

## Core Idea
This project builds a high-frequency navigation engine that minimizes inhaled pollution exposure for cyclists, joggers, and open-vehicle users by combining:

- Live environmental nowcasting (Sentinel-5P + ERA5/GFS + traffic spikes)
- Physics-informed GNN toxicity propagation on road graphs
- Gale-Shapley stable matching for equilibrium routing
- Rust/WASM A* for low-latency personalized pathfinding

## Repository Architecture

- `backend/`: FastAPI services, ingestion, PI-GNN, matching, routing, and workers
- `frontend/`: React-based visualization and demo UI
- `rust-router/`: Rust A* engine compiled to WASM
- `infra/`: Redis and local infrastructure configs
- `docs/`: Technical documents, architecture and design notes
- `data/`: Raw, processed, and cache data directories
- `scripts/`: Local developer scripts
- `notebooks/`: Exploration notebooks

## Quick Start (Prototype)

1. Start Redis:
   - `docker compose -f infra/docker-compose.yml up -d`
2. Backend setup:
   - `cd backend`
   - `python -m venv .venv`
   - `.venv\\Scripts\\activate`
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload`
3. Frontend setup:
   - `cd frontend`
   - `npm install`
   - `npm run dev`

## Phase-1 Deliverables

- Live 100m physics grid state in Redis
- Dynamic `Cedge` road toxicity estimation on a Bangalore subgraph
- Mode-aware route results using `W = sum(Cedge * te * IRmode)`
- Batch stable allocation of simulated commuters across green corridors

## License

MIT
