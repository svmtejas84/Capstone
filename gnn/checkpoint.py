from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from gnn.model import STPIGNN


DEFAULT_CHECKPOINT_PATH = Path("citywide_stpignn_best.pt")


@dataclass(frozen=True)
class STPIGNNCheckpointInfo:
    path: Path
    epoch: int | None
    best_val_mse: float | None
    loss_total: float | None
    note: str | None
    tensor_count: int
    node_in_dim: int
    edge_dim: int
    spatial_hidden_dim: int
    temporal_hidden_dim: int
    gnn_layers: int


def _state_dict_from_checkpoint(checkpoint: dict[str, Any]) -> dict[str, torch.Tensor]:
    state = checkpoint.get("state_dict")
    if not isinstance(state, dict):
        raise ValueError("Checkpoint does not contain a 'state_dict' dictionary")
    return state


def infer_stpignn_architecture(state_dict: dict[str, torch.Tensor]) -> dict[str, int]:
    """Infer the STPIGNN constructor arguments from a saved state dict."""
    required = [
        "node_encoder.weight",
        "gnn_layers.0.lin.weight",
        "gru.weight_ih_l0",
        "head.weight",
    ]
    missing = [key for key in required if key not in state_dict]
    if missing:
        raise ValueError(f"Checkpoint is missing required tensors: {missing}")

    node_encoder = state_dict["node_encoder.weight"]
    edge_projection = state_dict["gnn_layers.0.lin.weight"]
    gru_weight = state_dict["gru.weight_ih_l0"]
    head_weight = state_dict["head.weight"]

    gnn_layers = 0
    while f"gnn_layers.{gnn_layers}.eps" in state_dict:
        gnn_layers += 1

    return {
        "node_in_dim": int(node_encoder.shape[1]),
        "edge_dim": int(edge_projection.shape[1]),
        "spatial_hidden_dim": int(node_encoder.shape[0]),
        "temporal_hidden_dim": int(head_weight.shape[1]),
        "gnn_layers": int(gnn_layers),
        "gru_layers": int(gru_weight.shape[0] // (3 * head_weight.shape[1])),
    }


def load_stpignn_checkpoint(
    checkpoint_path: str | Path = DEFAULT_CHECKPOINT_PATH,
    device: str | torch.device = "cpu",
    eval_mode: bool = True,
) -> tuple[STPIGNN, STPIGNNCheckpointInfo]:
    """Load the trained ST-PIGNN checkpoint and reconstruct its architecture."""
    path = Path(checkpoint_path)
    if not path.exists():
        raise FileNotFoundError(f"ST-PIGNN checkpoint not found: {path}")

    checkpoint = torch.load(path, map_location=device, weights_only=False)
    if not isinstance(checkpoint, dict):
        raise ValueError(f"Unsupported checkpoint payload type: {type(checkpoint)!r}")

    state_dict = _state_dict_from_checkpoint(checkpoint)
    arch = infer_stpignn_architecture(state_dict)
    model = STPIGNN(
        node_in_dim=arch["node_in_dim"],
        edge_dim=arch["edge_dim"],
        spatial_hidden_dim=arch["spatial_hidden_dim"],
        temporal_hidden_dim=arch["temporal_hidden_dim"],
        gnn_layers=arch["gnn_layers"],
        gru_layers=arch["gru_layers"],
    ).to(device)
    model.load_state_dict(state_dict)
    if eval_mode:
        model.eval()

    info = STPIGNNCheckpointInfo(
        path=path,
        epoch=int(checkpoint["epoch"]) if "epoch" in checkpoint else None,
        best_val_mse=float(checkpoint["best_val_mse"]) if "best_val_mse" in checkpoint else None,
        loss_total=float(checkpoint["loss_total"]) if "loss_total" in checkpoint else None,
        note=str(checkpoint["note"]) if "note" in checkpoint else None,
        tensor_count=sum(1 for value in state_dict.values() if torch.is_tensor(value)),
        node_in_dim=arch["node_in_dim"],
        edge_dim=arch["edge_dim"],
        spatial_hidden_dim=arch["spatial_hidden_dim"],
        temporal_hidden_dim=arch["temporal_hidden_dim"],
        gnn_layers=arch["gnn_layers"],
    )
    return model, info
