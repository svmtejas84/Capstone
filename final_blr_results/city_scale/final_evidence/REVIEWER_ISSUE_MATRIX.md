# Reviewer issue matrix

| Issue | Evidence and closure | Status |
|---|---|---|
| Station forecast versus statistical baselines | Five-horizon corrected v2j benchmark; fixed any-model win only h1/3/24 | MIXED |
| Neural architecture controls | v2k matched 35-test Holm contrasts; exploratory intermediate-horizon advantages, h24 null | MIXED |
| Simple MLP and TCN controls | v2m 50/50 cells; ST-PIGNN versus TCN no Holm-surviving advantage; weather protocols differ | MIXED |
| Physics contribution and mechanism | v2l h3/6/12 predictive association, mixed seed/Laplacian/PVR behavior; no conservation/Q | MIXED predictive; UNSUPPORTED specificity |
| Held-out spatial transfer | v2j W6 has no neural WIN over ridge; 11 scored stations and four unscored | UNSUPPORTED superiority |
| Road graph engineering | v2k 154,902 nodes, 393,089 raw edges, 424,550 message arcs, one component | SUPPORTED structural integrity |
| Citywide concentration and compute | Corrected checkpoint and road-node features missing; no full-city forward pass or benchmark | BLOCKED / INCONCLUSIVE |
| Input explanation | v2n Captum MLP/TCN IG completed, 85/228 completeness flags; corrected ST-PIGNN weights absent | MIXED / ST-PIGNN UNVERIFIABLE |
| Exposure-aware routing | Legacy field/scaling and paired-validation gaps remain; no dose/time or capacity proof | UNSUPPORTED |
| Independence and reproducibility | Repeated Bengaluru test exposure; local ZIPs verified, external USB unverified; missing corrected neural weights | PARTIAL |

The exact claim classifications, source artifacts, allowed wording and prohibited wording are in `CLAIM_EVIDENCE_MATRIX.csv`. This matrix does not revise historical primary gates or write a research paper.
