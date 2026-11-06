# Results verification ledger

## Verification performed

Values in this package are traced to round-specific saved reports and machine-readable summary tables. The v2m ZIP archive contains all 50 individual MLP/TCN prediction parquet files. Independently recomputed 50 individual cells, 10 five-seed ensembles, and the 10 frozen ST-PIGNN-versus-MLP/TCN paired MAE deltas from the archived arrays. All 240 individual/ensemble metric checks match within 5e-6 (pair counts exact; maximum absolute difference 3.82e-6), and paired MAE deltas match the saved frozen table within 2.81e-8 on all 14,583 pairs. Raw predictions are retained in the existing archive; they were read in-memory, not extracted or modified. v2l per-seed and comparison CSVs are included without changing frozen families. v2r decoder metrics were recomputed from its 14,583-pair LOSO parquet; all three pooled methods match the saved summary within floating-point precision (maximum absolute difference < 8×10⁻¹⁵ for RMSE/MAE; R² < 6×10⁻¹⁷).

Recomputed v2m paired MAE contrasts across the predeclared ten family from archived five-seed predictions: all 10 deltas match the saved table within 2.81×10⁻⁸ µg/m³, relative improvements within 2.16×10⁻⁷ percentage points, with exact 14,583-pair counts. The archive members were read in-memory. The frozen confidence intervals, sign-flip p-values and Holm corrections remain sourced from the saved primary comparison table; they were not recalculated under a new family.

No discrepancy was repaired silently. If manuscript source PDFs/reviews or source-level data are transferred later, the matrices and bibliographic audit require a versioned supplement. Negative R² and unscored stations are retained.

## Interpretation limits

MAE/RMSE/R² describe the stated observed-monitor populations only. Repeated station-time rows do not increase independent spatial-site count. Retrospective interpolation, forecasting, road graph structure, citywide execution, explainability, and routing software are distinct evidence types.
