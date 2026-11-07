# Original directional loss audit

## Exact computational operation

The original notebook's cell 7 computes projected edge bearings as `atan2(dy, dx)` in mathematical degrees (east is 0°), then delegates a mask to `compute_dynamic_upwind_mask_vectorized`. That helper adds 180° to each edge bearing and compares the result to `current_wind_dir_deg` with a ±37.5° cone. Cell 13 sets that value from `xb[0,0,0,6]`: first batch, first time, first node, channel 6. The notebook does not demonstrate that this transformed feature value is unscaled meteorological degrees or spatially/time representative. Cell 20 reuses the same mask and calls positive downwind differences a “physical violation,” with a threshold of 0.05 in normalized/model-output units.

For active directed edge `u→v`, `src=u`, `dst=v`, the preserved legacy helper computes:

`d_uv = p_v - p_u`;

`w_uv = sigmoid(sum_k(edge_attr[u,v,k] / 1000))` when the edge-attribute length agrees with E, else `w_uv=1`;

`L_hinge = mean_active( max(0, w_uv d_uv)^2 )`.

The training loop adds `lambda(epoch) * L_hinge`, with `lambda(epoch)=lambda_max*min(1, epoch/25)`. The reported v2l corrected study is a distinct implementation: its wind-FROM direction is converted to transport-to, bearing is compass clockwise from north, and only its corrected length feature supplies the geometric sigmoid. Do not conflate those versions.

The hinge penalizes positive prediction differences in the selected direction. It has no time derivative, control-volume integral, face-normal flux, source/sink, boundary accounting, or cell volume. Penalty values inherit the model output's normalized target scale; the original notebook does not convert it to a dimensionally consistent physical mass rate. Summation over edge attributes inside a sigmoid is also not a calibrated transport coefficient. Its gradient pushes paired endpoint predictions toward a chosen monotonic ordering. That is a graph regularizer, not a conservation law.

## Relation to Gaussian plume formulation

The repository has a separate analytic `gnn/plume_physics.py::gaussian_plume(q,x,y,u,sigma_y,sigma_z,...)`. It needs emission rate `q` in µg/s, wind speed in m/s, dispersion widths in m and release height in m; the returned idealized concentration is µg/m³. The original directional hinge does not evaluate this equation, does not use its Q term, and does not solve the plume equation. The presence of plume utilities or a notebook visualization does not make the loss plume-informed or mass-conserving.

## Orientation caution

The intended corrected v2l convention is clear: meteorological wind is FROM; transport is `(wind_from+180) mod 360`; selected graph edges are aligned source-to-destination with transport; positive `p_dst-p_src` is the penalized increase. In the legacy notebook, the channel-6 scaling/meaning and bearing convention are not validated. Even if the mask selected exactly the intended downwind edges, requiring nonincreasing concentration downwind is only a heuristic and is not generally implied by a source-driven plume.

Source code: notebook cells 7, 13, 20; `src/stpignn/legacy_canonical.py`; corrected comparator `src/stpignn/physics_v2.py`; v2l full derivation `final_blr_results/physics_audit/methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md`.
