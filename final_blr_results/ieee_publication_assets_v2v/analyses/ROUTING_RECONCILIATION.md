# Routing utilization and scenario reconciliation

The saved v2t routing benchmark has four concentration fields: `original`, `uniform_125`, `spatial_sine`, and `support_distance`. Thus prose saying “three prespecified fields” refers to the three perturbations; it omits the original reference field. The full benchmark has four scenarios, each with three seeds, three demand levels (12, 24, 48), and six route/allocator methods.

| Scope | Scenario | Batch | Maximum utilization |
|---|---|---|---:|
| Original concentration field, all methods/batches | original | seed 37, demand 48 | 0.045918 = **4.5918%** |
| All four fields, all methods/batches | spatial_sine | seed 11, demand 48 | 0.054054 = **5.4054%** |

Both values are correct for different scopes. The v2u F08 caption used the all-scenario maximum while the source CSV/T07 was filtered to the original scenario. v2v F08 now reports 4.5918% for the original field and explicitly calls out 5.4054% as the global maximum under spatial-sine perturbation. `source_data/F08_capacity_by_scenario.csv` retains scenario/method maxima and `F08_utilization_reconciliation.csv` records the exact batch rows.

The saved “perturbation stability” table contains only three alternatives because it compares each of the three perturbations against the original. Total concentration fields = one original + three prespecified alternatives = four. The perturbations are stress scenarios, not calibrated uncertainty distributions.
