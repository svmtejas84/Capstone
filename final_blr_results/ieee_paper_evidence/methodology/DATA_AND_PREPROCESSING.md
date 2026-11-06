# Data and preprocessing evidence

Authoritative detail is version-specific. Corrected station forecasting uses a 15-station observed PM2.5 setting, 12-hour histories, observed targets, and versioned 18-channel inputs. v2j and v2m weather aggregation/alignment are not interchangeable: v2m's cutoff-safe MLP/TCN protocol differs from historical ST-PIGNN weather inputs. Retain the documented v2j/v2m distinction; historical weather investigations are not reopened here.

Do not substitute road nodes for monitors. Road-node PM2.5 is not observed. Original notebook features contained duplicated channels and target-hour leakage; those inputs are historical-only. Synthetic northing-derived elevation is not terrain. v2r decoder used verified SRTM elevation under its stated pipeline. Full provenance and source hashes are recorded in round-specific methodology and manifests, especially `final_blr_results/final_research_v2r/reproducibility/`.

Dataset provenance is incomplete for manuscript-level reproduction wherever source downloads/versions or full raw inputs are not retained; classify those fields as UNVERIFIABLE rather than inferring them.
