# Physics regularization evidence

The implemented term is a wind-direction eligibility mask over directed edges, a geometric edge-length factor, a rectified directional concentration-difference hinge squared, normalized over eligible edge/time contributions, and a scheduled global λ. Exact mask sign/orientation and implementation are in `final_blr_results/physics_audit/methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md` and configuration/code references there. v2l compares λ=0 and generic Laplacian controls; v2p/v2r add binary and continuous reliability gates.

The penalty does not implement mass conservation, the full advection–diffusion equation, or a validated dimensioned emissions source Q. A reduced violation metric is not proof of physical validity. Favorable h=6 and unfavorable h=24 effects both belong in any account. RGDR predictive effect is NOT EVALUATED; its novelty is NOT ESTABLISHED.
