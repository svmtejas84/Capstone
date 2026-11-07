"""Small 1-D finite-volume conservation verification; synthetic only.

Cell concentration is ug/m^3, cross-section is m^2, dx is m, and volume is
m^3. Face flux is ug/(m^2 s), source is ug/(m^3 s), and removal is s^-1.
Uses conservative upwind advection and centered diffusive face fluxes.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np


def rhs(c, dx, area, velocity, diffusivity, source=0.0, removal=0.0):
    c = np.asarray(c, dtype=np.float64)
    right = np.roll(c, -1)
    left = np.roll(c, 1)
    adv_face = velocity * (c if velocity >= 0 else right)
    diff_face = -diffusivity * (right - c) / dx
    flux_right = adv_face + diff_face
    flux_left = np.roll(flux_right, 1)
    return -(flux_right - flux_left) / dx + source - removal * c


def run():
    area = 4.0
    # Constant field and closed periodic-domain mass conservation.
    c0 = np.full(64, 12.5)
    assert np.max(np.abs(rhs(c0, 10.0, area, 2.0, 0.5))) == 0.0
    mass0 = c0.sum() * 10.0 * area
    c = c0.copy()
    dx, u, d, dt = 10.0, 2.0, 0.5, 0.5
    for _ in range(200):
        c += dt * rhs(c, dx, area, u, d)
    mass_rel_error = abs(c.sum() * dx * area - mass0) / mass0
    assert mass_rel_error < 1e-12

    # Known periodic 1-D translation: first-order upwind error must decrease.
    adv_errors = []
    for n in (64, 128, 256):
        length, u, t_end = 1.0, 0.7, 0.2
        dx = length / n
        x = (np.arange(n) + 0.5) * dx
        initial = 1.0 + 0.4 * np.sin(2 * np.pi * x / length)
        c = initial.copy()
        dt = 0.8 * dx / u
        steps = int(np.ceil(t_end / dt))
        dt = t_end / steps
        for _ in range(steps):
            c += dt * rhs(c, dx, 1.0, u, 0.0)
        exact = 1.0 + 0.4 * np.sin(2 * np.pi * ((x - u * t_end) % length) / length)
        adv_errors.append(float(np.mean(np.abs(c - exact))))
    assert adv_errors[2] < adv_errors[1] < adv_errors[0]

    # Diffusion of a periodic Fourier mode against its analytic exponential.
    diff_errors = []
    for n in (64, 128, 256):
        length, diffusivity, t_end = 1000.0, 4.0, 1000.0
        dx = length / n
        x = (np.arange(n) + 0.5) * dx
        k = 2 * np.pi / length
        c = 20.0 + 3.0 * np.sin(k * x)
        dt = 0.4 * dx * dx / diffusivity
        steps = int(np.ceil(t_end / dt))
        dt = t_end / steps
        for _ in range(steps):
            c += dt * rhs(c, dx, 1.0, 0.0, diffusivity)
        exact = 20.0 + 3.0 * np.exp(-diffusivity * k * k * t_end) * np.sin(k * x)
        diff_errors.append(float(np.mean(np.abs(c - exact))))
    assert diff_errors[2] < diff_errors[1] < diff_errors[0]

    # Uniform source/removal equilibrium S=k*C.
    c_eq = np.full(32, 8.0)
    source, removal = 0.16, 0.02
    eq_residual = float(np.max(np.abs(rhs(c_eq, 5.0, area, 0.0, 0.0, source, removal))))
    assert eq_residual < 1e-14

    # Nonperiodic boundary accounting identity for arbitrary boundary fluxes.
    n, dx, dt, area = 10, 2.0, 0.1, 3.0
    c = np.full(n, 5.0)
    face_flux = np.zeros(n + 1)
    face_flux[0], face_flux[-1] = 0.7, 0.2  # positive orientation left to right
    dc = -(face_flux[1:] - face_flux[:-1]) / dx
    dm_observed = float(np.sum((c + dt * dc) - c) * dx * area)
    dm_expected = float(dt * area * (face_flux[0] - face_flux[-1]))
    boundary_error = abs(dm_observed - dm_expected)
    assert boundary_error < 1e-12

    result = {
        "scope": "synthetic numerical verification only; not atmospheric validation",
        "method": "1-D conservative finite-volume, first-order upwind advection, centered diffusion, explicit Euler",
        "tolerances": {"mass_relative": 1e-12, "equilibrium_residual": 1e-14, "boundary_mass_ug": 1e-12,
                       "convergence": "strictly decreasing L1 error at each 2x grid refinement"},
        "constant_field_max_rhs_ug_m3_s": float(np.max(np.abs(rhs(c0, 10.0, area, 2.0, 0.5)))),
        "closed_periodic_mass_relative_error": mass_rel_error,
        "advection_grid_n": [64, 128, 256], "advection_l1_errors_ug_m3": adv_errors,
        "diffusion_grid_n": [64, 128, 256], "diffusion_l1_errors_ug_m3": diff_errors,
        "source_sink_equilibrium_max_residual_ug_m3_s": eq_residual,
        "boundary_net_mass_error_ug": boundary_error,
        "units": {"concentration": "ug/m^3", "cell_volume": "m^3", "face_flux": "ug/(m^2 s)",
                  "source": "ug/(m^3 s)", "removal": "s^-1", "integrated_mass": "ug"},
        "gradients": "not applicable; diagnostic uses NumPy finite-volume solver, no autograd",
    }
    out = Path(__file__).resolve().parent / "NUMERICAL_TEST_RESULTS.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
