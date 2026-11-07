# Numerical conservation diagnostic results

Command: `python final_blr_results/final_three_pillars/physics/conservation_diagnostic.py`. Machine-readable output: `NUMERICAL_TEST_RESULTS.json`.

| Test | Result | Tolerance |
|---|---:|---:|
| Constant concentration, periodic domain RHS | 0 µg m⁻³ s⁻¹ | exact zero |
| Closed periodic advective-diffusive mass relative error | 0 | < 1e−12 |
| 1-D advection L1 error, n=64 / 128 / 256 | 2.7716e−3 / 1.2115e−3 / 5.5894e−4 µg/m³ | strictly decreasing |
| Diffusion Fourier-mode L1 error, n=64 / 128 / 256 | 2.8974e−4 / 7.2317e−5 / 1.8072e−5 µg/m³ | strictly decreasing |
| Uniform source/removal equilibrium residual | 0 µg m⁻³ s⁻¹ | < 1e−14 |
| Nonperiodic net boundary mass identity error | 2.14e−15 µg | < 1e−12 |

The discretization accounts for source/sink dimensions and boundary flux. The periodic test is a synthetic closed-domain case. The solver uses NumPy and is not differentiable; autograd checks are not applicable. CFL/diffusion stability limits are respected by selected explicit time steps in the test harness. No real weather, emissions, diffusivity, concentration grid, or road geometry enters.

**Interpretation:** the conservative finite-volume arithmetic is verified for these synthetic cases. Empirical atmospheric mass conservation is **not evaluated**. The historical ST-PIGNN loss remains a directional prediction regularizer.
