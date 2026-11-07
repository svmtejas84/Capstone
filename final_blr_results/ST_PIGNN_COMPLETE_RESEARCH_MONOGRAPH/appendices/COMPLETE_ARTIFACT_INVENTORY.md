# Complete artifact inventory

The v2k integrity census is included in this monograph at [`tables/v2k_archive_integrity.csv`](../tables/v2k_archive_integrity.csv): 2,141 inventoried artifacts and 318 unmatched result files at its 2026-11-05 snapshot. It is a historical census, not a claim that all later v2m–v2t files were already present. Source SHA-256: `6916e3295ff346d8b48eff3ea599c0a997edb4bfa55376d77115a169a5f42297`; copied content differs only by CRLF-to-LF line-ending normalization.

Later rounds are separately represented by the complete source coverage CSV, the following manifests and the copied results tables. Missing checkpoint classes and external backup remain explicitly unresolved.

| Round | Inventory source | Status |
|---|---|---|
| baselines | `final_blr_results/baselines/v2m/reproducibility/RESEARCH_RESULTS_v2m_MANIFEST.csv` | present; SHA-256 `a95a8768183e4c8820595f6cce37f549f19318059357a3ce2b87eab403b79d84` |
| city_scale | `final_blr_results/city_scale/reproducibility/artifact_checksums.csv` | present; SHA-256 `a0e163caaa4cf07870bf418f3e67c59749a638b77c2884a1ee14ce9aef2ca829` |
| final_research_v2r | `final_blr_results/final_research_v2r/reproducibility/artifact_checksums.csv` | present; SHA-256 `cd5bce699b6c4a9b3a93d77c7eed10b14e3ca2239a1db83b5bcb1efbbed9e9e0` |
| final_three_pillars | `final_blr_results/final_three_pillars/reproducibility/CHECKSUMS.csv` | present; SHA-256 `e919bceba9f6ac0cb9e215fd0e5dfc9a94976ed6e2894e85c67cebecfd1b6997` |
| final_routing_closure | `final_blr_results/final_routing_closure/v2t/reproducibility/checksums.csv` | present; SHA-256 `a38dc15cc24280af8d3de984de6cc9a05a87c3728c7fa2fa99cd6b55c2188099` |
