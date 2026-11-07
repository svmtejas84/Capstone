# Complete equation register

All equations identify the implementation generation or diagnostic they describe. The source files cited after each formula fix the precise tensor convention. Concentration \(C\) has units µg/m³ unless a normalized predictor is stated.

## 1. Observed-target station forecast

For station \(i\), issue time \(t\), horizon \(h\), and observed-target mask \(m_{i,t+h}\), a masked empirical loss is

$$L_{\mathrm{data}}=\frac{\sum_{i,t}m_{i,t+h}\ell(\hat y_{i,t+h},y_{i,t+h})}{\sum_{i,t}m_{i,t+h}}.$$

The 12-hour input window must end no later than issue time \(t\). A missing observation is never a measured zero. The corrected log1p-compatible residual anchor and scale are dataset-version-specific. Evidence: src/stpignn/data_v2.py; IEEE evidence training methodology.

## 2. Edge-aware GINE and temporal GRU

For latent node vector \(x_i\), encoded edge vector \(e_{ji}\), and graph neighborhood \(N(i)\):

$$x_i'=\operatorname{MLP}\!\left((1+\epsilon)x_i+\sum_{j\in N(i)}\operatorname{ReLU}(x_j+e_{ji})\right).$$

One standard recurrent formulation is

$$z_t=\sigma(W_zx_t+U_zh_{t-1}+b_z),\quad r_t=\sigma(W_rx_t+U_rh_{t-1}+b_r),$$
$$\tilde h_t=\tanh(W_hx_t+U_h(r_t\odot h_{t-1})+b_h),\quad h_t=(1-z_t)\odot\tilde h_t+z_t\odot h_{t-1}.$$

The library implementation, block order, dimensions and graph topology must be read from gnn/model.py, src/stpignn/models_v2.py or src/stpignn/models_v3.py for the corresponding model version.

## 3. Directional hinge

With eligible directed-edge mask \(M_{ij,t}\), geometric factor \(g_{ij}\), normalized forecast \(\hat y\), and denominator safeguard \(\epsilon\), the schematic regularizer is

$$L_{\mathrm{dir}}=\frac{\sum_{(i,j),t}M_{ij,t}g_{ij}[\max(0,\hat y_{j,t}-\hat y_{i,t})]^2}{\sum_{(i,j),t}M_{ij,t}+\epsilon}.$$

This is a monotonicity heuristic. The exact executed mask orientation, geometric factor, normalization and warm-up are in src/stpignn/physics_v2.py and the v2l physics methodology. It is not a mass balance.

## 4. Continuous reliability gate

For eligible past-observation age \(\Delta_i(t)\), fixed \(\tau=4\) h, and maximum lookback 24 h:

$$q_i(t)=\begin{cases}\exp[-\Delta_i(t)/\tau],&\text{eligible observation exists},\\0,&\text{otherwise},\end{cases}
\qquad r_{ij,t}=q_i(t)q_j(t).$$

The gate weights the directional loss; it does not calibrate uncertainty. Binary V1 instead uses observed/imputed provenance. Evidence: v2p and v2r RGDR specifications.

## 5. Finite-volume diagnostic

For atmospheric control volume \(V_i\) m³, concentration \(C_i\) µg/m³, time step \(\Delta t\) h, advective and diffusive face fluxes \(F_f\) µg/h, and source/removal rates \(S_i,R_i\) µg/(m³ h):

$$V_i\frac{C_i^{n+1}-C_i^n}{\Delta t}+\sum_{f\in\partial i}(F_f^{\mathrm{adv}}+F_f^{\mathrm{diff}})=V_i(S_i-R_i).$$

Synthetic tests validate this standalone discretization, not historical ST-PIGNN checkpoints. Evidence: final_three_pillars/physics/CONSERVATION_FORMULATION.md.

## 6. Station-to-road interpolation

For eligible station estimates \(\hat C_i\), query coordinate \(q\), distance \(d(q,i)\), and fixed exponent \(p\):

$$\hat C(q)=\frac{\sum_i w_i(q)\hat C_i}{\sum_i w_i(q)},\qquad w_i(q)=d(q,i)^{-p}.$$

A zero-distance rule and station-exclusion fold are required. Retrospective observed-field IDW and forecast-IDW are distinct tasks. Evidence: v2o spatial estimation method and v2r spatial methodology.

## 7. Modeled inhaled dose and edge quotas

For edge concentration \(C_e\) µg/m³, respiratory minute-volume converted to rate \(R\) m³/h, edge length \(L_e\) m and speed \(v\) m/h:

$$D_e=C_eR\frac{L_e}{v}\quad[\mu\mathrm g].$$

The corrected allocator checks every directed edge \(e\) after each proposal and at termination:

$$\sum_{u:e\in R_u}d_{u,e}\le K_e.$$

Here \(d_{u,e}=1\) simulated commuter in v2t and \(K_e\) is an assumed declared quota, not measured road capacity. Evidence: final_routing_closure/v2t/CAPACITY_ALLOCATOR_SPECIFICATION.md.

## 8. Integrated Gradients

For scalar forecast \(F(x)\), input \(x\), baseline \(x'\), and feature index \(k\):

$$IG_k(x;x')=(x_k-x'_k)\int_0^1\frac{\partial F(x'+\alpha(x-x'))}{\partial x_k}\,d\alpha.$$

Completeness compares \(\sum_k IG_k\) with \(F(x)-F(x')\); baseline choice changes attribution. This is not proof of causal atmospheric transport. Evidence: final_three_pillars/captum/IG_METHODOLOGY.md.
