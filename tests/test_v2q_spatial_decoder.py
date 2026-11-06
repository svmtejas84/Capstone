import importlib.util
from pathlib import Path

import pytest
import torch


MODULE = Path(__file__).resolve().parents[1] / "final_blr_results/citywide_extension/v2q/spatial_decoder.py"
spec = importlib.util.spec_from_file_location("v2q_spatial_decoder", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_support_permutation_and_exact_site():
    xy = torch.tensor([[0.0, 0.0], [1000.0, 0.0], [0.0, 1000.0]])
    y = torch.tensor([10.0, 20.0, 30.0])
    q = torch.tensor([[0.0, 0.0], [500.0, 500.0]])
    a, d = mod.forecast_idw(xy, y, q)
    b, _ = mod.forecast_idw(xy[[2, 0, 1]], y[[2, 0, 1]], q)
    assert a[0] == pytest.approx(10.0)
    assert d[0] == pytest.approx(0.0)
    assert torch.allclose(a, b)


def test_no_support_and_invalid_inputs_fail_closed():
    xy = torch.empty((0, 2))
    with pytest.raises(ValueError):
        mod.forecast_idw(xy, torch.empty(0), torch.zeros((1, 2)))
    with pytest.raises(ValueError):
        mod.forecast_idw(torch.zeros((1, 2)), torch.tensor([float("nan")]), torch.zeros((1, 2)))


def test_untrained_decoder_is_idw_and_has_finite_gradients():
    xy = torch.tensor([[0.0, 0.0], [1000.0, 0.0]])
    forecast = torch.tensor([15.0, 35.0], requires_grad=True)
    elevation = torch.tensor([900.0, 910.0])
    q = torch.tensor([[250.0, 0.0], [750.0, 0.0]])
    model = mod.CompactSpatialDecoder()
    out, nearest = model(xy, forecast, elevation, q, torch.tensor([902.0, 908.0]))
    baseline, _ = mod.forecast_idw(xy, forecast, q)
    assert torch.allclose(out, baseline)
    assert torch.all(nearest > 0)
    out.sum().backward()
    assert torch.isfinite(forecast.grad).all()
    assert sum(p.numel() for p in model.parameters()) == 1249
