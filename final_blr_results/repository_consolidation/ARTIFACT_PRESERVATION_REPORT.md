# Artifact preservation before main integration

The audit inventoried **22 named key artifacts**, **16 local ZIP archives**, and **272 local weight-like files**. Per-file SHA-256 and Git state are recorded in `KEY_ARTIFACT_HASHES.csv` and `LOCAL_ARCHIVE_HASHES.csv`. Seven local-only key artifacts were extracted by streaming their ZIP members and confirmed byte-identical in `ARCHIVE_MEMBER_MATCHES.csv`: road nodes, road edges, historical 64-partition tensor, one v2r fold checkpoint, one full-city prediction snapshot, and both corrected Captum tensor variants. No original artifact was modified to perform this check.

| Artifact family | Preservation status | Consequence |
|---|---|---|
| Original notebook, corrected scripts, physics/RGDR/routing source, research reports, monograph, IEEE evidence/assets, London handover | Tracked by Git | Included in source-history integration; authoritative scientific interpretations remain in reports |
| Historical checkpoint examples | Some tracked directly (138 local weight-like files) | Git contains these specific objects; check model/protocol compatibility separately |
| Canonical road nodes/edges and partition tensor | Ignored, host-local; byte-identical to local pre-v2m ZIP | Not delivered by Git; ZIP is on the same host |
| v2r fold weights and citywide prediction arrays | Untracked/ignored; representative files byte-identical to local v2r ZIP | Not delivered by Git; no independent roadside validation follows |
| Corrected Captum tensors | Ignored; both representative variants byte-identical to local three-pillar ZIP | Not delivered by Git; saved figures/tables are tracked |
| v2j run controls and old benchmark outputs | Pre-existing untracked/ignored, preserved in primary checkout | Do not clean or stage wholesale |
| Sixteen local research ZIPs | Eight untracked, eight ignored | Exact SHA-256 in CSV; same-host archives only |
| Independent USB/cloud artifact copy | **NOT VERIFIED** | Source bundle and Git push are not complete data backup |

The source Git bundle planned after synchronization preserves commit history and refs, not ignored/raw datasets or ZIPs. No large datasets, checkpoints or archives are newly committed merely to make `main` appear complete.
