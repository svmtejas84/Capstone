# Matching formulation and guarantees

## Serving route matching

Let commuters be (C), route candidates (R), route capacity (q_r\in\mathbb{Z}_{\ge1}), and each commuter (c) rank a finite ordered list of routes. Each route (r) ranks commuters. The implementation is the usual commuter-proposing deferred-acceptance loop for a many-to-one market: an unmatched commuter proposes to their next route; a route holds the best (q_r) applicants so far and rejects/displaces the rest.

For the API, commuter route utility is ranked by

\[
s_{cr}=\alpha_m\frac{D_r}{\max_{j\in R}D_j}+(1-\alpha_m)\frac{L_r}{\ell_c},
\]

where (D_r\) is modeled inhaled mass, (L_r\) route length, ℓ_c is distance tolerance, and α_m is mode dependent. Lower is preferred. The route receiver score is

\[
v_{rc}=\frac{w_{m(c)}+1/\mathrm{idmin}_c}{1+\max(0,\gamma_r)},
\]

ranked higher first (ties broken by commuter ID); current API uses γ_r=0. The route quota is independently estimated from the minimum edge class/lane capacity, a 900 s window and route-duration discount; it is not a shared-link allocation model.

## Classical theorem boundary

For finite commuters and routes, complete strict preferences over mutually acceptable pairs, fixed route quotas, responsive route preferences (a route chooses its top (q_r) applicants), and no post-processing fallback, commuter-proposing deferred acceptance terminates after at most ∑_c |P_c| proposals. The result is feasible and stable in the standard many-to-one sense: no commuter-route pair both prefers each other to their assignment, with unmatched below every acceptable listed route. It is commuter-optimal among stable outcomes under those assumptions. These guarantees are limited to the abstract route quota, not physical road-edge capacity.

The API implementation's default (n\times |R|) loop bound is enough for unique complete preference lists, but the current fallback then assigns all remaining commuters without enforcing quota/acceptability. Therefore the actual function does **not** guarantee feasible or stable output when unmatched proposers remain. Equal default receiver ranks for omitted commuters also break the complete strict-preference assumptions unless lists are complete.

## Offline path-bundle allocator

For each route choice (p\), let (E(p)) be its set of directed road arcs and (q_e) the quota on arc (e). The allocator maintains selected commuters (x_c\in P_c\cup\{\varnothing\}) with

\[
\sum_c\mathbf 1[e\in E(x_c)]\le q_e\quad\forall e.
\]

This explicit set constraint provides ex-post feasibility because every overfull edge rejects enough applicants and each rejected path releases all its edge reservations before termination. Each commuter proposes to each finite option at most once, so the procedure terminates. It is not standard many-to-one matching: commuters demand bundles of edges, while each edge's ranking of a commuter depends on the commuter's current whole-route dose/time. The conditions required for standard deferred-acceptance stability—particularly substitutable choice—are not established. Feasibility does not imply pairwise stability, a core outcome, or social-welfare optimality.

## What is and is not guaranteed

| Property | API `batch_match` | Offline `deferred_acceptance` |
|---|---|---|
| Termination | Finite proposal list / n×m guard; finite in current API. | Finite options, each proposal advances a pointer. |
| Route quota feasibility | Only before fallback; fallback can overflow. | Edge quota feasibility enforced by path release and final assertion. |
| Shared-edge feasibility | Not representable. | Yes for the directed arcs and quotas supplied. |
| Individual rationality | Not guaranteed after fallback. | A selected route is a listed proposal; exhausted demand stays unmatched. |
| Standard matching stability | Only under complete strict preferences, responsive route choices and no fallback. | Not established for complementary path bundles. |
| Welfare / dose optimality | Not guaranteed; proposer-optimality only within stable outcomes under theorem assumptions. | Not guaranteed; local edge rankings are not a global objective. |
