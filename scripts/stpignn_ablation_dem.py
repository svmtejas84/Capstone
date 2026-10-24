"""SRTM mapping and a synthetic ablation harness for the paper STPIGNN.

Architecture, target scale, physics penalty and PVR convention follow
notebooks/production/evaluated_wind_advection.ipynb. Synthetic results are
implementation checks, not held-out Bangalore measurements.

Run ``python scripts/stpignn_ablation_dem.py`` for the mock ablation report.
To map the actual graph nodes, run with ``--download-dem`` and
``--nodes-parquet data/graphs/bangalore_utm_nodes.parquet``. DEM operations
require rasterio, pyproj and elevation; GDAL command line tools are optional.
For measured station-subset ablations, use ``--real-ablation --epochs 15``.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import gzip
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.amp import GradScaler, autocast
from torch.utils.data import DataLoader, Dataset
from torch_geometric.nn import GCNConv

from src.stpignn import STPIGNN
from src.stpignn.paths import REPO_ROOT as ROOT

BANGALORE_BOUNDS = (77.45, 12.80, 77.80, 13.15)  # W,S,E,N in EPSG:4326
REPORT_NAME = "ST_PIGNN_Ablation_Results_Nov2026.md"
TARGET_SCALE = 342.9356  # normalized PM2.5 -> micrograms/m^3, per notebook
DESCRIPTIONS = {
    "no_GRU": "GRU replaced by an nn.Linear projection of all 12 spatial time steps.",
    "no_GINE": "GINEConv replaced by GCNConv; edge features are unused by GCN.",
    "no_Physics": "Advection penalty weight lambda_t fixed at 0.0.",
    "no_Imputation": "Imputed node targets masked; batches with no observed targets omitted.",
}


def download_bangalore_dem(output: Path, bounds=BANGALORE_BOUNDS) -> Path:
    """Fetch SRTM1 (~30 m), with a rasterio path if GDAL CLI is unavailable.

    The fallback reads the same public Skadi HGT tiles used by ``elevation``.
    """
    import elevation
    import rasterio
    from rasterio.merge import merge

    west, south, east, north = bounds
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError("bounds must be west,south,east,north in EPSG:4326")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.exists():
        if shutil.which("gdal_translate") and shutil.which("gdalbuildvrt"):
            elevation.clip(bounds=bounds, output=str(output), product="SRTM1")
        else:
            with TemporaryDirectory(dir=output.parent) as temp_name:
                temp = Path(temp_name)
                tiles = []
                for lat in range(int(np.floor(south)), int(np.ceil(north))):
                    for lon in range(int(np.floor(west)), int(np.ceil(east))):
                        name = f"{'N' if lat >= 0 else 'S'}{abs(lat):02d}{'E' if lon >= 0 else 'W'}{abs(lon):03d}"
                        url = f"https://s3.amazonaws.com/elevation-tiles-prod/skadi/{name[:3]}/{name}.hgt.gz"
                        archive = temp / f"{name}.hgt.gz"
                        hgt = temp / f"{name}.hgt"
                        urlretrieve(url, archive)
                        with gzip.open(archive, "rb") as source, hgt.open("wb") as destination:
                            shutil.copyfileobj(source, destination)
                        tiles.append(rasterio.open(hgt))
                try:
                    pixels, transform = merge(tiles, bounds=bounds, nodata=-32768)
                    profile = tiles[0].profile.copy()
                    profile.update(driver="GTiff", height=pixels.shape[1], width=pixels.shape[2],
                                   count=1, transform=transform, nodata=-32768, compress="deflate")
                    staged = temp / "bangalore_srtm1.tif"
                    with rasterio.open(staged, "w", **profile) as dst:
                        dst.write(pixels)
                    os.replace(staged, output)
                finally:
                    for tile in tiles:
                        tile.close()
    with rasterio.open(output) as dem:
        if dem.crs is None or dem.count < 1:
            raise ValueError("DEM must have a CRS and at least one band")
    return output


def map_true_elevation(nodes_df: pd.DataFrame, dem_path: Path) -> pd.DataFrame:
    """Vectorized UTM 43N lookup; outside/NoData locations remain NaN."""
    import rasterio
    from rasterio.transform import rowcol
    from pyproj import Transformer

    if not {"utm_x", "utm_y"} <= set(nodes_df):
        raise ValueError("nodes_df must contain utm_x and utm_y")
    result = nodes_df.copy()
    xy = result[["utm_x", "utm_y"]].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    valid = np.isfinite(xy).all(axis=1)
    elevation_m = np.full(len(result), np.nan)
    with rasterio.open(dem_path) as dem:
        if dem.crs is None:
            raise ValueError("DEM lacks a CRS")
        transform = Transformer.from_crs("EPSG:32643", dem.crs, always_xy=True)
        x, y = transform.transform(xy[valid, 0], xy[valid, 1])
        finite = np.isfinite(x) & np.isfinite(y)
        positions = np.flatnonzero(valid)[finite]
        rows, cols = rowcol(dem.transform, np.asarray(x)[finite], np.asarray(y)[finite])
        rows, cols = np.asarray(rows), np.asarray(cols)
        inside = (rows >= 0) & (rows < dem.height) & (cols >= 0) & (cols < dem.width)
        band = dem.read(1, masked=True)
        sampled = np.ma.asarray(band[rows[inside], cols[inside]]).astype(float)
        elevation_m[positions[inside]] = sampled.filled(np.nan)
    result["elevation_true"] = elevation_m
    return result


def make_dummy_nodes(n: int = 154_902, seed: int = 42) -> pd.DataFrame:
    """Example 154,902-row DataFrame in UTM zone 43N."""
    from pyproj import Transformer

    rng = np.random.default_rng(seed)
    west, south, east, north = BANGALORE_BOUNDS
    lon, lat = rng.uniform(west, east, n), rng.uniform(south, north, n)
    x, y = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True).transform(lon, lat)
    return pd.DataFrame({"utm_x": x, "utm_y": y})


class NoGRU(STPIGNN):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gru = nn.Linear(12 * kwargs["spatial_hidden_dim"], kwargs["temporal_hidden_dim"])

    def forward(self, x_seq, edge_index, edge_attr):
        if x_seq.ndim == 3:
            x_seq = x_seq.unsqueeze(0)
        if x_seq.shape[1] != 12:
            raise ValueError("no_GRU expects the paper notebook's 12-step input window")
        spatial = torch.stack(
            [self._spatial_encode(x_seq[:, t], edge_index, edge_attr) for t in range(12)], dim=2
        )  # [batch, nodes, time, hidden]
        return self.head(self.dropout(self.gru(spatial.flatten(start_dim=2)))).squeeze(-1)


class NoGINE(STPIGNN):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        h = kwargs["spatial_hidden_dim"]
        self.gnn_layers = nn.ModuleList(GCNConv(h, h) for _ in range(kwargs["gnn_layers"]))

    def _spatial_encode(self, x_t, edge_index, edge_attr):
        batch, nodes, _ = x_t.shape
        x = self.node_encoder(x_t).reshape(batch * nodes, -1)
        edges = self._expand_edge_index_for_batch(edge_index, nodes, batch)
        for conv, norm in zip(self.gnn_layers, self.norms):
            x = x + self.dropout(torch.relu(norm(conv(x, edges))))
        return x.reshape(batch, nodes, -1)


@dataclass
class GraphSample:
    x_seq: torch.Tensor  # [T,N,16]
    target: torch.Tensor  # normalized PM2.5 [N]
    sensor_mask: torch.Tensor  # observed target mask [N]
    edge_index: torch.Tensor  # [2,E]
    edge_attr: torch.Tensor  # [E,D]
    edge_bearings: torch.Tensor  # degrees [E]
    is_imputed: bool | torch.Tensor  # item flag or per-node target provenance
    wind_degrees: float | None = None
    target_time: pd.Timestamp | None = None


class GraphSamples(Dataset):
    def __init__(self, samples, drop_imputed=False):
        self.samples = []
        for sample in samples:
            if drop_imputed and isinstance(sample.is_imputed, torch.Tensor):
                sample = replace(sample, sensor_mask=sample.sensor_mask & ~sample.is_imputed)
                if not bool(sample.sensor_mask.any()):
                    continue
            elif drop_imputed and sample.is_imputed:
                continue
            self.samples.append(sample)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        return self.samples[index]


def synthetic_samples(count: int, seed: int) -> list[GraphSample]:
    rng = np.random.default_rng(seed)
    src = np.arange(11)
    edges = torch.tensor(np.stack([np.r_[src, src + 1], np.r_[src + 1, src]]), dtype=torch.long)
    attr = torch.tensor(np.tile([100.0, 0.0], (22, 1)), dtype=torch.float32)
    bearings = torch.tensor(np.r_[np.zeros(11), np.full(11, 180.0)], dtype=torch.float32)
    samples = []
    for i in range(count):
        x = rng.normal(size=(12, 12, 16)).astype(np.float32)
        x[..., 6] = 0.0  # valid bearing that also stays in the scaled feature range
        y = np.maximum(0.01, 0.2 + 0.05 * x[-1, :, 0] + 0.02 * x[-2, :, 1])
        samples.append(GraphSample(torch.from_numpy(x), torch.from_numpy(y),
                                   torch.ones(12, dtype=torch.bool), edges, attr,
                                   bearings, is_imputed=(i % 4 == 0)))
    return samples


def real_station_samples(train_count: int = 64, validation_count: int = 24):
    """Build chronological real-data windows on the 15 mapped PM2.5 stations.

    Input features are the notebook's 16 channels. The target is the following
    hour, which avoids putting that target directly in the input window.
    Training can use imputed targets; validation scores observed targets only.
    A four-neighbor station graph uses actual UTM coordinates and DEM heights.
    """
    base = ["pm2_5_scaled", "pm10_scaled", "nitrogen_dioxide_scaled",
            "sulphur_dioxide_scaled", "carbon_monoxide_scaled", "wind_speed_10m_scaled",
            "wind_direction_10m_scaled", "wind_gusts_10m_scaled",
            "temperature_2m_scaled", "relative_humidity_2m_scaled", "surface_pressure_scaled"]
    columns = ["time", "node_index", "parameter", "value", "observed_value",
               "is_imputed", "wind_direction_10m"] + base
    frame = pd.read_parquet(ROOT / "data/processed/graph/master_scaled_checkpoint.parquet",
                            columns=columns)
    frame = frame.loc[frame.parameter == "pm25"].sort_values(["time", "node_index"])
    node_ids = np.sort(frame.node_index.unique())
    times = pd.DatetimeIndex(np.sort(frame.time.unique()))
    n = len(node_ids)
    if len(frame) != len(times) * n or frame.duplicated(["time", "node_index"]).any():
        raise ValueError("PM2.5 station timeline is incomplete or duplicated")
    feature11 = frame[base].to_numpy(dtype=np.float32).reshape(len(times), n, 11)
    features = np.concatenate([feature11, feature11[..., [2, 3, 0, 1, 4]]], axis=-1)
    values = frame.value.to_numpy(dtype=np.float32).reshape(len(times), n)
    observed = (~frame.is_imputed.to_numpy(dtype=bool)).reshape(len(times), n)
    wind = frame.wind_direction_10m.to_numpy(dtype=np.float32).reshape(len(times), n)

    mapping = pd.read_parquet(ROOT / "data/processed/graph/topology_nodeid_to_index_map.parquet")
    coords = pd.read_parquet(ROOT / "data/processed/graph/nodes_elevation_true.parquet")
    station_ids = mapping.set_index("node_index").loc[node_ids, "node_id"].to_numpy()
    station = coords.set_index("osmid").loc[station_ids]
    xy = station[["utm_x", "utm_y"]].to_numpy(dtype=np.float32)
    z = station.elevation_true.to_numpy(dtype=np.float32)
    distance = np.linalg.norm(xy[:, None, :] - xy[None, :, :], axis=-1)
    np.fill_diagonal(distance, np.inf)
    source = np.repeat(np.arange(n), min(4, n - 1))
    dest = np.argsort(distance, axis=1)[:, :min(4, n - 1)].reshape(-1)
    dx, dy = xy[dest, 0] - xy[source, 0], xy[dest, 1] - xy[source, 1]
    bearings = (np.degrees(np.arctan2(dy, dx)) + 360.0) % 360.0
    edge_features = np.zeros((len(source), 16), dtype=np.float32)
    edge_features[:, 0] = np.linalg.norm(xy[dest] - xy[source], axis=1)
    edge_features[:, 1:3] = xy[dest] - xy[source]
    edge_features[:, 3] = z[dest] - z[source]
    edges = torch.tensor(np.stack([source, dest]), dtype=torch.long)
    attrs = torch.from_numpy(edge_features)
    bearings_t = torch.from_numpy(bearings.astype(np.float32))

    # Require 12 consecutive hourly history steps followed by the target hour.
    hourly = np.diff(times.to_numpy(dtype="datetime64[ns]").astype("int64")) == 3_600_000_000_000
    candidates = np.flatnonzero(np.convolve(hourly.astype(int),
                                           np.ones(12, dtype=int), mode="valid") == 12) + 12
    split = int(len(times) * 0.8)
    valid_target = np.isfinite(values) & (values >= 0) & (values <= 500)
    candidates = candidates[(valid_target[candidates] & observed[candidates]).any(axis=1)]

    def choose(indices, count, *, validation):
        if len(indices) < count:
            raise ValueError(f"Only {len(indices)} eligible {'validation' if validation else 'training'} windows")
        selected = indices[np.linspace(0, len(indices) - 1, count, dtype=int)]
        samples = []
        for i in selected:
            mask = valid_target[i] & observed[i] if validation else valid_target[i]
            samples.append(GraphSample(
                x_seq=torch.from_numpy(features[i - 12:i].copy()),
                target=torch.from_numpy((values[i] / TARGET_SCALE).copy()),
                sensor_mask=torch.from_numpy(mask.copy()), edge_index=edges,
                edge_attr=attrs, edge_bearings=bearings_t,
                is_imputed=torch.from_numpy((~observed[i]).copy()),
                wind_degrees=float(np.nanmedian(wind[i])) % 360.0,
                target_time=pd.Timestamp(times[i]),
            ))
        return samples, (str(times[selected[0]]), str(times[selected[-1]]))

    train, train_range = choose(candidates[candidates < split], train_count, validation=False)
    validation, validation_range = choose(candidates[candidates >= split], validation_count,
                                          validation=True)
    metadata = {"nodes": n, "edges": len(source), "train_windows": train_count,
                "validation_windows": validation_count, "train_range": train_range,
                "validation_range": validation_range,
                "validation_targets": sum(int(s.sensor_mask.sum()) for s in validation)}
    return train, validation, metadata


def upwind_mask(bearings: torch.Tensor, wind_degrees: float) -> torch.Tensor:
    reverse = (bearings + 180.0) % 360.0
    angle = torch.abs(reverse - wind_degrees)
    return torch.minimum(angle, 360.0 - angle) <= 37.5  # notebook's 75-degree cone


def advection_penalty(pred, edges, selected, edge_attr):
    if not bool(selected.any()):
        return pred.new_zeros(())
    src, dst = edges[:, selected]
    resistance = torch.sigmoid((edge_attr[selected] / 1000.0).sum(dim=-1))
    return torch.relu((pred[dst] - pred[src]) * resistance).square().mean()


def evaluate(model, samples, device) -> dict[str, float]:
    model.eval()
    absolute = squared = 0.0
    n_targets = n_violations = n_edges = 0
    with torch.no_grad():
        for sample in samples:
            x = sample.x_seq.unsqueeze(0).to(device)
            edge, attr = sample.edge_index.to(device), sample.edge_attr.to(device)
            pred = model(x, edge, attr).float().view(-1)
            mask = sample.sensor_mask.to(device)
            error = (pred[mask] - sample.target.to(device)[mask]) * TARGET_SCALE
            absolute += error.abs().sum().item()
            squared += error.square().sum().item()
            n_targets += int(mask.sum().item())
            wind = sample.wind_degrees if sample.wind_degrees is not None else float(x[0, 0, 0, 6])
            selected = upwind_mask(sample.edge_bearings.to(device), wind)
            if bool(selected.any()):
                src, dst = edge[:, selected]
                n_violations += int(((pred[dst] - pred[src]) > 0.05).sum().item())
                n_edges += int(selected.sum().item())
    if n_targets == 0 or n_edges == 0:
        raise ValueError("Validation needs observed targets and upwind edges")
    return {"MAE": absolute / n_targets, "RMSE": (squared / n_targets) ** 0.5,
            "PVR": 100 * n_violations / n_edges}


def run_ablations(train_samples, validation_samples, epochs=1, device=None, hidden_dim=96):
    if not train_samples or not validation_samples or epochs < 1:
        raise ValueError("Supply nonempty samples and positive epochs")
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    args = dict(node_in_dim=16, edge_dim=train_samples[0].edge_attr.shape[1],
                spatial_hidden_dim=hidden_dim, temporal_hidden_dim=hidden_dim, gnn_layers=2)
    results = {}
    for variant in DESCRIPTIONS:
        print(f"Training {variant} for {epochs} epochs on {len(train_samples)} windows...", flush=True)
        torch.manual_seed(42)
        model = {"no_GRU": NoGRU, "no_GINE": NoGINE}.get(variant, STPIGNN)(**args).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=3e-6, weight_decay=1e-2)
        scaler = GradScaler("cuda", enabled=device.type == "cuda")
        dataset = GraphSamples(train_samples, drop_imputed=variant == "no_Imputation")
        if not len(dataset):
            raise ValueError("No training items remain after imputation filtering")
        loader = DataLoader(dataset, batch_size=1, collate_fn=lambda batch: batch[0])
        for epoch in range(1, epochs + 1):
            model.train()
            lambda_t = 0.0 if variant == "no_Physics" else 0.060 * min(1.0, epoch / 25.0)
            for sample in loader:
                x = sample.x_seq.unsqueeze(0).to(device)
                y, mask = sample.target.to(device), sample.sensor_mask.to(device)
                edge, attr = sample.edge_index.to(device), sample.edge_attr.to(device)
                wind = sample.wind_degrees if sample.wind_degrees is not None else float(x[0, 0, 0, 6])
                selected = upwind_mask(sample.edge_bearings.to(device), wind)
                optimizer.zero_grad(set_to_none=True)
                with autocast(device_type=device.type, dtype=torch.float16, enabled=device.type == "cuda"):
                    pred = model(x, edge, attr).view(-1)
                    data_loss = (pred[mask] - y[mask]).square().mean() if bool(mask.any()) else pred.new_zeros(())
                    physics_loss = advection_penalty(pred, edge, selected, attr) if lambda_t else pred.new_zeros(())
                    loss = data_loss + lambda_t * physics_loss
                if not torch.isfinite(loss):
                    raise FloatingPointError(f"Nonfinite loss for {variant}")
                if loss.requires_grad:
                    scaler.scale(loss).backward()
                    scaler.unscale_(optimizer)
                    nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.3)
                    scaler.step(optimizer)
                    scaler.update()
        results[variant] = evaluate(model, validation_samples, device)
        print(f"Finished {variant}: {results[variant]}", flush=True)
    return results


def write_markdown_report(results, metadata, output=ROOT / REPORT_NAME) -> Path:
    lines = ["# ST-PIGNN Ablation Results", "", f"- Run type: {metadata['run_type']}",
             f"- Executed (UTC): {metadata['timestamp_utc']}", f"- Device: {metadata['device']}",
             f"- Epochs per variant: {metadata['epochs']}",
             "- MAE/RMSE: µg/m³. PVR: upwind edges with normalized difference > 0.05.",
             "", "| Model variant | MAE | RMSE | PVR | Architectural change |",
             "| --- | ---: | ---: | ---: | --- |"]
    if metadata["run_type"] == "observed station subset":
        lines[7:7] = [f"- Graph: {metadata['nodes']} mapped sensor nodes, {metadata['edges']} directed four-neighbor edges.",
                      f"- Train: {metadata['train_windows']} windows, {metadata['train_range'][0]} to {metadata['train_range'][1]}.",
                      f"- Validation: {metadata['validation_windows']} windows, {metadata['validation_range'][0]} to {metadata['validation_range'][1]}.",
                      f"- Observed validation targets: {metadata['validation_targets']}.",
                      "- Validation uses observed PM2.5 targets only; targets outside 0–500 µg/m³ are excluded.",
                      "- This station subset uses a distance-based graph and is not the paper's 154,902-node citywide evaluation."]
    for variant, description in DESCRIPTIONS.items():
        metric = results[variant]
        lines.append(f"| {variant} | {metric['MAE']:.4f} | {metric['RMSE']:.4f} | "
                     f"{metric['PVR']:.2f}% | {description} |")
    if metadata["run_type"] == "synthetic demonstration":
        lines += ["", "These scores are from synthetic samples and are not paper findings."]
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-dem", action="store_true")
    parser.add_argument("--dem", type=Path, default=ROOT / "data/dem/bangalore_srtm1.tif")
    parser.add_argument("--nodes-parquet", type=Path, help="UTM nodes, with utm_x/utm_y or x/y")
    parser.add_argument("--mapped-nodes", type=Path, default=ROOT / "data/processed/graph/nodes_elevation_true.parquet")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--real-ablation", action="store_true", help="Train on chronological observed station windows")
    parser.add_argument("--train-windows", type=int, default=64)
    parser.add_argument("--validation-windows", type=int, default=24)
    parser.add_argument("--report", type=Path, default=ROOT / REPORT_NAME)
    opts = parser.parse_args()
    if opts.download_dem:
        download_bangalore_dem(opts.dem)
    if opts.nodes_parquet:
        nodes = pd.read_parquet(opts.nodes_parquet).rename(columns={"x": "utm_x", "y": "utm_y"})
        mapped = map_true_elevation(nodes, opts.dem)
        opts.mapped_nodes.parent.mkdir(parents=True, exist_ok=True)
        mapped.to_parquet(opts.mapped_nodes, index=False)
        print(f"Mapped {mapped.elevation_true.notna().sum():,}/{len(mapped):,} nodes to {opts.mapped_nodes}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if opts.real_ablation:
        train, validation, details = real_station_samples(opts.train_windows, opts.validation_windows)
        run_type = "observed station subset"
    else:
        train, validation, details = synthetic_samples(8, 42), synthetic_samples(3, 2026), {}
        run_type = "synthetic demonstration"
    results = run_ablations(train, validation, epochs=opts.epochs, device=device)
    metadata = {"run_type": run_type, "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "device": torch.cuda.get_device_name(device) if device.type == "cuda" else str(device),
                "epochs": opts.epochs, **details}
    print(f"Wrote {write_markdown_report(results, metadata, opts.report)}")


if __name__ == "__main__":
    main()
