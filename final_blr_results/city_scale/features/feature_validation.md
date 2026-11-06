# Feature and checkpoint gate

| Required item | Verified state | Verdict |
|---|---|---|
| Station input, 12 × 18 and 15 monitored nodes | Corrected v2j/v2m arrays and builder document it | COMPATIBLE for their own station protocols |
| Road tensor x and edge attributes | Static 17 channels; 16 road length/category edge channels | BLOCKED for direct corrected station-model use |
| Complete cutoff-aligned road-node pollutant history | Stored at only 22 road nodes; 154,880 absent | BLOCKED |
| Residual PM2.5 anchor at unmonitored road nodes | No observed history or validated estimate | BLOCKED |
| Citywide differentiated weather with source grid provenance | One known raw source coordinate; no source-grid mapping | UNVERIFIABLE |
| Corrected v2j ST-PIGNN/λ0/Laplacian weights | Saved predictions exist, matching neural checkpoints not archived | UNVERIFIABLE for IG; BLOCKED for city inference |
| v2m MLP/TCN weights | 50 matching station-model checkpoints and cutoff-safe array | COMPATIBLE for station-only IG after wrapper check; BLOCKED for graph inference |
| Legacy root citywide and `results/checkpoints_v2*` weights | Different historical protocols and no demonstrated corrected feature/scaler equivalence | APPROXIMATE WITH ASSUMPTIONS as historical artifacts; BLOCKED as corrected substitutes |

**Overall corrected full-city compatibility: BLOCKED.** No small, medium or full road-subgraph predictive forward pass is admissible under the frozen gate. Numerical shape or V100 capacity cannot repair missing source features and checkpoint lineage. Existing road-node PM2.5 fields are legacy/imputed features, not 154,902 observed labels. The v2m station-only checkpoint path remains viable for descriptive IG of MLP/TCN, without implying any ST-PIGNN physics explanation.
