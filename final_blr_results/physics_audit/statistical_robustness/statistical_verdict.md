# Statistical robustness verdict

The ensemble physics−λ=0 MAE differences at h=1,3,6,12,24 are respectively −0.026, −0.130, −0.410, −0.262, +0.145 µg/m³. The original 35-comparison Holm family retains adjusted evidence at h=3,6,12 only. A retrospective five-horizon physics family also retains h=3,6,12, but it cannot convert this exposed test set into confirmatory evidence (`multiplicity_analysis.csv`).

| h | UTC-day 95% CI | Seven-calendar-day block 95% CI | Months favoring physics |
|---:|---:|---:|---:|
| 1 | [−0.050,−0.001] | [−0.068,+0.015] | 4/7 |
| 3 | [−0.210,−0.055] | [−0.252,−0.042] | 6/7 |
| 6 | [−0.550,−0.274] | [−0.632,−0.209] | 6/7 |
| 12 | [−0.381,−0.139] | [−0.451,−0.076] | 6/7 |
| 24 | [−0.013,+0.314] | [−0.064,+0.342] | 1/7 |

Seven-day blocks widen intervals; h=1 no longer excludes zero, while h=3/6/12 remain negative. Monthly signs are not universal: February is unfavorable at h=3/6, January at h=12. The five largest absolute day sums account for 13–20% of total absolute day effect by horizon; they influence, but do not alone create, the h=3/6/12 pooled benefit. `monthly_effects.csv` retains every month and pair count; `multiplicity_analysis.csv` records the exact top-day contribution. Dependence, one-season coverage and repeated test use remain limitations.
