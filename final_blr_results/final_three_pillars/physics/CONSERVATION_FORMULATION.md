# Conservation-aware formulation and data gate

A physically dimensioned passive-tracer balance over a control volume Ω is:

`∂C/∂t + ∇·(u C) = ∇·(K ∇C) + S - k C`,

where C is µg/m³, velocity u is m/s, diffusivity tensor K is m²/s, volumetric source S is µg/(m³ s), and first-order removal k is s⁻¹. Integrating over cell Ωᵢ of volume Vᵢ gives:

`d/dt ∫Ωᵢ C dV = - Σ_f A_f [(u C - K∇C)·n]_f + ∫Ωᵢ S dV - ∫Ωᵢ k C dV`.

For finite volume, each internal face must use one shared flux with opposite signs in its two adjacent cell balances. Closed-domain global mass conservation follows by cancellation of internal fluxes and zero net boundary flux, and only if source/removal terms are also accounted.

## Required inputs and current status

| Term | Required data | Bengaluru availability / status |
|---|---|---|
| Cell geometry | Non-overlapping 2-D/3-D cells, face areas, normals, volumes, valid CRS and mesh-to-observation mapping | Road graph has nodes/links, not atmospheric cells/faces; no justified road-to-air control-volume construction. **Unavailable**. |
| Initial and evolving concentration | Time-resolved cell concentration field with calibrated observation operator | Station observations are sparse; road-node outputs are estimates, not independent concentration observations. **Insufficient**. |
| Advection | Spatially/temporally resolved wind vector at modeled height, forecast-causal alignment | Station meteorology is sparse and does not resolve street-level flow. **Incomplete/estimated**. |
| Diffusion | Turbulent diffusivity tensor or a calibrated closure varying in space/time | No validated citywide K field or calibration. **Missing**. |
| Source | Emission rate/location/speciation, preferably time-resolved traffic/inventory, units µg/s | No validated Q field. Synthetic northing is not terrain; no emissions values may be invented. **Missing**. |
| Boundary flux | Inflow/outflow and boundary concentration or a justified boundary condition | Not established for a city-air domain. **Missing**. |
| Removal | Deposition/chemistry/settling terms with coefficients and units | No validated removal field. **Missing**. |
| Time integration | Observation interval, forecast dt, stable discretization and measurement alignment | Station series exists but cannot repair absent grid/flux terms. |

Road links are transportation geometry, not atmospheric cell faces. A road-edge graph must not be used as a finite-volume mesh without a separate physical construction and validation. The right path is a separately reviewed domain/mesh and data proposal; no new neural training is needed to verify the numerical scheme.

The implemented synthetic 1-D diagnostic uses conservative upwind advection, centered diffusive face flux, explicit Euler, periodic boundaries for analytic convergence, and an explicitly accounted nonperiodic boundary-flux identity. It tests algebra and numerical behavior only. It is not a Bengaluru atmospheric solver and does not retroactively alter any ST-PIGNN result.
