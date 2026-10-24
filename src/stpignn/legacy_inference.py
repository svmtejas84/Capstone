"""Legacy routing adapter; preserved only for Phase A parity.

The feature builder below is incompatible with data_v2 and must not be used
for new routing experiments.
"""
from gnn.checkpoint import load_stpignn_checkpoint
from gnn.stpignn_inference import _build_temporal_x_seq, TARGET_SCALE, TARGET_PM25_MAX

__all__ = ["load_stpignn_checkpoint", "_build_temporal_x_seq", "TARGET_SCALE", "TARGET_PM25_MAX"]
