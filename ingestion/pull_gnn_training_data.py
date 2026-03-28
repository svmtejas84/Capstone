from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from gnn.edge_weights import compute_edge_weights
from ingestion.data_fusion import fuse_weather_and_airquality
from ingestion.redis_publisher import get_latest_airquality, get_latest_sensors, get_latest_weather
from shared.config import get_settings
from shared.redis_client import RedisStore


def _edge_keys() -> list[tuple[int, int]]:
	keys = sorted(compute_edge_weights(np.ones((8, 8), dtype=float)).keys())
	if not keys:
		raise RuntimeError("No edge keys were produced by compute_edge_weights")
	return keys


def build_gnn_dataset(samples: int, seed_start: int = 1000) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
	"""Generate tensors for GNN training from ingestion snapshots.

	Returns:
		features: [N, 4, H, W] concentration + wind_u + wind_v + source_spike
		targets: [N, E] edge weight targets in sorted edge order
		edge_index: [E, 2] edge node pairs aligned with targets
	"""
	if samples <= 0:
		raise ValueError("samples must be > 0")

	edges = _edge_keys()
	edge_index = np.array(edges, dtype=np.int64)
	settings = get_settings()
	store = RedisStore()
	store.connect()

	features: list[np.ndarray] = []
	targets: list[np.ndarray] = []

	for i in range(samples):
		weather = get_latest_weather(store)
		airquality = get_latest_airquality(store)
		sensors = get_latest_sensors(store)
		payload = fuse_weather_and_airquality(weather, airquality, sensors, settings)
		concentration = np.array(payload["concentration"], dtype=np.float32)
		wind_u = np.array(payload["wind_u"], dtype=np.float32)
		wind_v = np.array(payload["wind_v"], dtype=np.float32)
		source_spike = np.array(payload["source_spike"], dtype=np.float32)

		edge_map = compute_edge_weights(concentration, wind_u=wind_u, wind_v=wind_v)
		target_vec = np.array([float(edge_map[e]) for e in edges], dtype=np.float32)

		features.append(np.stack([concentration, wind_u, wind_v, source_spike], axis=0))
		targets.append(target_vec)

	return np.stack(features, axis=0), np.stack(targets, axis=0), edge_index


def save_gnn_dataset(output_dir: Path, samples: int, seed_start: int = 1000) -> tuple[Path, Path]:
	output_dir.mkdir(parents=True, exist_ok=True)
	features, targets, edge_index = build_gnn_dataset(samples=samples, seed_start=seed_start)

	timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
	npz_path = output_dir / f"gnn_training_dataset_{timestamp}.npz"
	meta_path = output_dir / f"gnn_training_dataset_{timestamp}.json"

	np.savez_compressed(npz_path, features=features, targets=targets, edge_index=edge_index)

	metadata = {
		"created_at": timestamp,
		"samples": int(samples),
		"seed_start": int(seed_start),
		"features_shape": list(features.shape),
		"targets_shape": list(targets.shape),
		"edge_index_shape": list(edge_index.shape),
		"feature_channels": ["concentration", "wind_u", "wind_v", "source_spike"],
	}
	meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
	return npz_path, meta_path


def main() -> None:
	parser = argparse.ArgumentParser(description="Generate GNN training dataset from ingestion snapshots")
	parser.add_argument("--samples", type=int, default=200, help="Number of samples to generate")
	parser.add_argument("--seed-start", type=int, default=1000, help="Start seed for deterministic sampling")
	parser.add_argument("--output-dir", type=Path, default=Path("data/gnn"), help="Output directory")
	args = parser.parse_args()

	npz_path, meta_path = save_gnn_dataset(
		output_dir=args.output_dir,
		samples=args.samples,
		seed_start=args.seed_start,
	)
	print(f"saved_dataset={npz_path}")
	print(f"saved_metadata={meta_path}")


if __name__ == "__main__":
	main()
