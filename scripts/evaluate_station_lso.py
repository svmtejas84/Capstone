"""Five-fold leave-station-out ST-PIGNN and spatial baselines on observed PM2.5.

Run: python scripts/evaluate_station_lso.py --epochs 5
Outputs are written under data/processed/evaluations/.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold
from sklearn.metrics.pairwise import euclidean_distances

from src.stpignn import STPIGNN
from src.stpignn.paths import REPO_ROOT as ROOT
from scripts.stpignn_ablation_dem import TARGET_SCALE, real_station_samples

OUT = ROOT / "data/processed/evaluations"


def station_coordinates() -> tuple[np.ndarray, np.ndarray]:
    frame = pd.read_parquet(ROOT / "data/processed/graph/master_scaled_checkpoint.parquet",
                            columns=["parameter", "node_index"])
    ids = np.sort(frame.loc[frame.parameter.eq("pm25"), "node_index"].unique())
    if len(ids) != 15:
        raise ValueError(f"Expected 15 physical PM2.5 stations, found {len(ids)}")
    mapping = pd.read_parquet(ROOT / "data/processed/graph/topology_nodeid_to_index_map.parquet")
    nodes = pd.read_parquet(ROOT / "data/processed/graph/nodes_elevation_true.parquet")
    osmids = mapping.set_index("node_index").loc[ids, "node_id"].to_numpy()
    xy = nodes.set_index("osmid").loc[osmids, ["utm_x", "utm_y"]].to_numpy(float)
    if not np.isfinite(xy).all():
        raise ValueError("Station coordinates must be finite UTM metres")
    return ids, xy


def metrics(y: list[float], p: list[float]) -> dict:
    if not y:
        return {"n": 0, "mae": None, "rmse": None, "r2": None}
    return {"n": len(y), "mae": float(mean_absolute_error(y, p)),
            "rmse": float(np.sqrt(mean_squared_error(y, p))),
            "r2": float(r2_score(y, p)) if len(y) > 1 and np.var(y) > 0 else None}


def idw(x_known: np.ndarray, y_known: np.ndarray, x_query: np.ndarray, power: float = 2) -> np.ndarray:
    distance = euclidean_distances(x_query, x_known)
    weights = 1 / np.maximum(distance, 1e-6) ** power
    return weights @ y_known / weights.sum(axis=1)


def kriging(x_known: np.ndarray, y_known: np.ndarray, x_query: np.ndarray) -> np.ndarray:
    """Ordinary kriging via a constant-mean Gaussian process with spatial RBF covariance."""
    # Coordinates in km prevent poorly conditioned kernel length scales.
    center = x_known.mean(axis=0)
    kernel = ConstantKernel(1.0, constant_value_bounds="fixed") * RBF(5.0, length_scale_bounds="fixed") + WhiteKernel(0.05, noise_level_bounds="fixed")
    model = GaussianProcessRegressor(kernel=kernel, alpha=1e-5, optimizer=None, normalize_y=True)
    model.fit((x_known - center) / 1000, y_known)
    return model.predict((x_query - center) / 1000)


def run(epochs: int, train_windows: int, validation_windows: int, seed: int, device: str) -> dict:
    torch.manual_seed(seed)
    np.random.seed(seed)
    ids, xy = station_coordinates()
    train, validation, meta = real_station_samples(train_windows, validation_windows)
    history = pd.read_parquet(ROOT / "data/processed/graph/master_scaled_checkpoint.parquet",
                              columns=["parameter", "time", "node_index", "value", "is_imputed"])
    history = history.loc[history.parameter.eq("pm25")].set_index(["time", "node_index"])
    if len(train[0].target) != 15:
        raise ValueError("Station sample order does not match 15 physical stations")
    folds = KFold(n_splits=5, shuffle=True, random_state=seed)
    rows, predictions = [], []
    dev = torch.device(device)
    for fold, (known, hidden) in enumerate(folds.split(ids), 1):
        known_t = torch.as_tensor(known, dtype=torch.long)
        hidden_t = torch.as_tensor(hidden, dtype=torch.long)
        # The training graph is induced by the 12 known stations. Hidden nodes
        # have no features, labels, or messages in any optimizer step.
        edge = train[0].edge_index
        train_edges = torch.isin(edge[0], known_t) & torch.isin(edge[1], known_t)
        local = torch.full((15,), -1, dtype=torch.long)
        local[known_t] = torch.arange(len(known_t))
        e_train = local[edge[:, train_edges]].to(dev)
        a_train = train[0].edge_attr[train_edges].to(dev)
        # Query edges point from known nodes into held-out nodes. There is no
        # reverse path from hidden observations to known node embeddings.
        query_edges = torch.isin(edge[0], known_t) & torch.isin(edge[1], hidden_t)
        e_val = edge[:, train_edges | query_edges].to(dev)
        a_val = train[0].edge_attr[train_edges | query_edges].to(dev)
        if not bool(query_edges.any()):
            raise ValueError("No known-to-hidden message-passing edges")
        model = STPIGNN(node_in_dim=16, edge_dim=a_train.shape[1],
                        spatial_hidden_dim=32, temporal_hidden_dim=32, gnn_layers=2).to(dev)
        optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-3)
        for epoch in range(epochs):
            model.train()
            for sample in train:
                # Only physical observations count as labels; imputed values
                # remain excluded from the training loss.
                mask = sample.sensor_mask[known_t] & ~sample.is_imputed[known_t]
                if not bool(mask.any()):
                    continue
                x = sample.x_seq[:, known_t, :].unsqueeze(0).to(dev)
                target = sample.target[known_t].to(dev)
                optimizer.zero_grad(set_to_none=True)
                pred = model(x, e_train, a_train).view(-1)
                loss = (pred[mask.to(dev)] - target[mask.to(dev)]).square().mean()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
            print(f"Fold {fold}/5 epoch {epoch + 1}/{epochs}", flush=True)
        model.eval()
        ys = {name: [] for name in ("gnn", "idw", "kriging")}
        ps = {name: [] for name in ys}
        with torch.no_grad():
            for sample_index, sample in enumerate(validation):
                observed_hidden = hidden[(sample.sensor_mask[hidden] & ~sample.is_imputed[hidden]).numpy()]
                # Use physical station readings at the final input hour,
                # never the next-hour target or an imputed reading.
                prior_hour = sample.target_time - pd.Timedelta(hours=1)
                prior = history.loc[[(prior_hour, int(ids[node])) for node in known], ["value", "is_imputed"]]
                known_values_all = prior.value.to_numpy(dtype=float)
                available = (~prior.is_imputed.to_numpy(dtype=bool)) & np.isfinite(known_values_all) & (known_values_all >= 0) & (known_values_all <= 500)
                observed_known = known[available]
                if len(observed_known) < 3 or not len(observed_hidden):
                    continue
                # Suppress all station-derived channels at hidden nodes across
                # the 12 input hours, including duplicated pollutant channels.
                x = sample.x_seq.clone()
                x[:, hidden_t[:, None], torch.tensor([0, 1, 2, 3, 4, 11, 12, 13, 14, 15])] = 0
                gnn_pred = model(x.unsqueeze(0).to(dev), e_val, a_val).view(-1).cpu().numpy() * TARGET_SCALE
                targets = sample.target[observed_hidden].numpy() * TARGET_SCALE
                known_values = known_values_all[available]
                estimates = {"gnn": gnn_pred[observed_hidden],
                             "idw": idw(xy[observed_known], known_values, xy[observed_hidden]),
                             "kriging": kriging(xy[observed_known], known_values, xy[observed_hidden])}
                for name, estimate in estimates.items():
                    for node, actual, predicted in zip(observed_hidden, targets, estimate):
                        ys[name].append(float(actual))
                        ps[name].append(float(predicted))
                        predictions.append({"fold": fold, "method": name, "sample_index": sample_index,
                                            "node_index": int(ids[node]), "actual_pm25": float(actual),
                                            "predicted_pm25": float(predicted)})
        for name in ys:
            rows.append({"fold": fold, "method": name, "held_out_node_indices": ",".join(map(str, ids[hidden])),
                         **metrics(ys[name], ps[name])})
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "station_lso_metrics.csv", index=False)
    pd.DataFrame(predictions).to_csv(OUT / "station_lso_predictions.csv", index=False)
    result = {"config": {"epochs": epochs, "train_windows": train_windows,
                         "validation_windows": validation_windows, "seed": seed,
                         "device": str(dev), "target_unit": "micrograms/m3", **meta}, "folds": rows}
    (OUT / "station_lso_results.json").write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--train-windows", type=int, default=96)
    parser.add_argument("--validation-windows", type=int, default=96)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()
    print(json.dumps(run(args.epochs, args.train_windows, args.validation_windows, args.seed, args.device)["folds"], indent=2))
