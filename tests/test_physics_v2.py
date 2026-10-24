import torch
import pytest

from src.stpignn.physics_v2 import (MissingTrafficIndex, corrected_wind_mask,
                                    emission_margin_normalized, pvr_statistics)


def test_west_wind_selects_eastbound_edge():
    xy = torch.tensor([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    edges = torch.tensor([[0, 1, 0], [1, 0, 2]])
    assert corrected_wind_mask(xy, edges, 270.0).tolist() == [True, False, False]


def test_pvr_thresholds_and_q():
    pred = torch.tensor([0.0, 0.2])
    edges = torch.tensor([[0], [1]])
    mask = torch.tensor([True])
    rows = pvr_statistics(pred, edges, mask, 100.0)
    assert [r["violations"] for r in rows] == [1, 1, 1, 1]
    rows_q = pvr_statistics(pred, edges, mask, 100.0, q_norm=torch.tensor([0.16]))
    assert [r["violations"] for r in rows_q] == [1, 1, 0, 0]


def test_q_requires_traffic_source():
    with pytest.raises(MissingTrafficIndex):
        emission_margin_normalized(None, 1.0, 100.0)
