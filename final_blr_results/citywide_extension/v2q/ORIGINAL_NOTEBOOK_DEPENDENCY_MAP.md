# Notebook dependency map (zero-based cell indices)

| Cells | Imports / source | External data or output | Risk / status |
|---|---|---|---|
| 0–1 | NumPy, pandas, torch, `src.stpignn`, `gnn.model`, `shared.physics_config` | root checkpoint saver | Configuration and save function; no saved outputs. |
| 2–3 | sklearn KMeans, `legacy_canonical.SpatialPartition` | topology PyG, node map, OSM UTM nodes | Geometry/topology valid; partitions drop boundary arcs. |
| 4–6 | pandas, `scipy.spatial.KDTree` | master scaled Parquet | Cell 5 supersedes cell 4 and copies complete pollutant timelines to missing nodes. |
| 7–8 | torch, legacy wind-mask port | partition edge bearings | First-node scaled wind direction later passed as degrees. |
| 9–10 | `legacy_canonical.TierAwareClusterDatasetV3`, DataLoader | model-input node-hour Parquet | Same-hour input/target and modulo timelines. |
| 11–12 | `gnn.model.STPIGNN` | graph edge dimension | 16×16 GINE–GRU checkpoint compatible. |
| 13 | legacy penalty and metric ports | `citywide_stpignn_{checkpoint_STABLE,best}.pt` | Training and checkpoint overwrite; do not execute. |
| 14 | Captum IG, `src.stpignn.explain` | best checkpoint | Historical explainability only. |
| 15–17 | sklearn metrics, torch | best checkpoint, CSV reports | Scores monitoring nodes only; one cell mixes train and validation. |
| 18–19 | scipy griddata, matplotlib | contour figures in notebook results | Plotting interpolates/averages model outputs; no valid city forecast. |
| 20–24 | legacy mask, baseline classes, metrics | best checkpoint, figures | PVR is a directional threshold statistic; cell 21 hard-codes spatial-decay values; cell 23 baseline models are instantiated but not trained. |
| 25 | empty | none | none. |

No Markdown cells or saved execution outputs exist. The notebook has no road-node observation generator, explicit forecast-origin builder, trained spatial decoder or routing optimizer. `gnn/stpignn_inference.py` is an external route-local helper and falls back to repeated static graph features if temporal construction fails; it is not a validated notebook citywide prediction path.
