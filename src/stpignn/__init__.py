"""Importable implementation extracted from the canonical production notebook."""

from gnn.model import STPIGNN
from .canonical import (TierAwareClusterDatasetV3, compute_dynamic_upwind_mask_vectorized,
                        compute_wind_advection_penalty, masked_mae_rmse_vectorized,
                        scored_mask)

__all__ = ["STPIGNN", "TierAwareClusterDatasetV3", "compute_dynamic_upwind_mask_vectorized",
           "compute_wind_advection_penalty", "masked_mae_rmse_vectorized", "scored_mask"]
