import numpy as np
import pytest
import torch

from src.stpignn.physics_v2 import batched_penalty, corrected_wind_mask
from src.stpignn.rgdr_continuous import (
    age_reliability, continuous_directional_penalty, fit_tau_train_only,
    observed_age_hours,
)


def test_cutoff_age_cannot_use_future_observation():
    obs = np.array([[False, False], [True, False], [False, True], [False, False], [True, True]])
    age = observed_age_hours(obs, np.array([0, 1, 2, 3]))
    assert np.isinf(age[0]).all()
    assert age[1, 0] == 0 and np.isinf(age[1, 1])
    assert age[2, 0] == 1 and age[2, 1] == 0
    assert age[3, 0] == 2 and age[3, 1] == 1
    changed = obs.copy(); changed[4] = False
    np.testing.assert_array_equal(observed_age_hours(changed, np.array([3])), age[[3]])


def test_reliability_units_bounds_and_missing():
    ages = torch.tensor([[0.0, 1.0, 24.0, 25.0, float("inf")]])
    q = age_reliability(ages, 2.0)
    assert q[0, 0] == pytest.approx(1.0)
    assert q[0, 1] == pytest.approx(np.exp(-0.5))
    assert q[0, 3] == 0 and q[0, 4] == 0
    assert torch.all((q >= 0) & (q <= 1))
    assert fit_tau_train_only(np.array([[0, 1, 3, np.inf, 25]], float)) == 2.0


def test_all_zero_age_equals_fixed_and_missing_has_finite_gradient():
    xy = torch.tensor([[0.0, 0.0], [1.0, 0.0]])
    edge = torch.tensor([[0, 1], [1, 0]])
    length = torch.tensor([[1000.0], [1000.0]])
    wind = corrected_wind_mask(xy, edge, 270.0)[None, :]
    assert wind.tolist() == [[True, False]]
    pred = torch.tensor([[1.0, 2.0]], requires_grad=True)
    fixed = batched_penalty(pred, edge, wind, length, "corrected_mask")
    new = continuous_directional_penalty(pred, edge, wind, length, torch.zeros((1, 2)), 2.0)
    assert new.detach().item() == pytest.approx(fixed.detach().item())
    missing = continuous_directional_penalty(pred, edge, wind, length,
                                               torch.full((1, 2), float("inf")), 2.0)
    (new + missing).backward()
    assert missing.detach().item() == 0 and torch.isfinite(pred.grad).all()


def test_constant_fractional_reliability_matches_fixed_when_normalized_mass_is_positive():
    # Eight eligible directed instances keep the unchanged clamp-at-one
    # denominator above one for q_src*q_dst = 0.25.
    edge = torch.tensor([[0] * 8, [1] * 8])
    length = torch.full((8, 1), 1000.0)
    mask = torch.ones((1, 8), dtype=torch.bool)
    pred = torch.tensor([[1.0, 3.0]])
    age = torch.full((1, 2), float(np.log(2.0)))
    fixed = batched_penalty(pred, edge, mask, length, "corrected_mask")
    gated = continuous_directional_penalty(pred, edge, mask, length, age, float(np.log(2.0)))
    assert gated.item() == pytest.approx(fixed.item())


def test_batched_normalization_and_reproducibility():
    edge = torch.tensor([[0], [1]])
    length = torch.tensor([[500.0]])
    mask = torch.ones((2, 1), dtype=torch.bool)
    p = torch.tensor([[1.0, 3.0], [2.0, 4.0]])
    age = torch.tensor([[0.0, 0.0], [float("inf"), float("inf")]])
    a = continuous_directional_penalty(p, edge, mask, length, age, 1.0)
    b = continuous_directional_penalty(p[:1], edge, mask[:1], length, age[:1], 1.0)
    assert a == pytest.approx(b.item())
    assert a == continuous_directional_penalty(p, edge, mask, length, age, 1.0)
