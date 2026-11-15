"""Generate reader-facing numerical LaTeX tables from the frozen V4 CSVs."""
from pathlib import Path
import pandas as pd
V=Path('final_blr_results/controlled_validation_v4_review_closure')
T=V/'tables';T.mkdir(exist_ok=True)
def table(path,headers,rows):
 with (T/path).open('w') as f:
  f.write('% Exploratory exposed Bengaluru test; MAE differences and CI bounds in micrograms per cubic metre.\n')
  f.write('\\begin{tabular}{'+'l'*(len(headers)-4)+'rrrr}\\hline\n')
  f.write(' & '.join(headers)+r' \\'+'\n\\hline\n')
  for row in rows:f.write(' & '.join(row)+r' \\'+'\n')
  f.write('\\hline\n\\end{tabular}\n')
def n(x):return f'{x:.3f}'
def p(x):return f'{x:.4f}'
a=pd.read_csv(V/'COMPLETE_20_CONTRAST_RESULTS.csv')
labels={'zero':'No regularization','shuffled_wind':'Within-month shuffle','rotated_wind':'+90$^\\circ$ rotated wind','laplacian':'Original Laplacian'}
rows=[]
for _,r in a.iterrows():
 v=r.contrast.removeprefix('true_wind_minus_')
 rows.append([str(int(r.horizon_hours)),labels[v],n(r.paired_delta_mae_ug_m3),n(r.ci95_low_ug_m3),n(r.ci95_high_ug_m3),p(r.holm_20_p)])
table('T1_20_WIND_CONTRASTS.tex',['h (hours)','Comparator','$\\Delta$MAE','$95\\%$ CI low','$95\\%$ CI high','Holm p'],rows)
a=pd.read_csv(V/'statistical_analysis/GRAPH_ARCHITECTURE_CONTRASTS.csv')
labels={'gru_only':'GRU-only','tcn':'Temporal CNN','mlp':'MLP'}
rows=[]
for _,r in a.iterrows():
 v=r.contrast.removeprefix('unregularized_GINE_GRU_minus_')
 rows.append([str(int(r.horizon_hours)),labels[v],n(r.paired_delta_mae_ug_m3),n(r.ci95_low_ug_m3),n(r.ci95_high_ug_m3),p(r.holm_15_p)])
table('T2_GRAPH_ARCHITECTURE.tex',['h (hours)','Comparator','$\\Delta$MAE','$95\\%$ CI low','$95\\%$ CI high','Holm p'],rows)
a=pd.read_csv(V/'statistical_analysis/V4_SIX_CONTRASTS.csv')
labels={'reverse_wind_006':'Reversed wind','constant_north_006':'Fixed north','full_shuffle_006':'Full-period shuffle','true_wind_03':'True wind, $\\lambda=0.3$','true_wind_10':'True wind, $\\lambda=1.0$','laplacian_matched':'Magnitude-matched Laplacian'}
rows=[]
for _,r in a.iterrows():
 v=r.contrast.removeprefix('true_wind_006_minus_')
 rows.append([labels[v],n(r.paired_delta_mae_ug_m3),n(r.ci95_low_ug_m3),n(r.ci95_high_ug_m3),p(r.holm_6_p)])
table('T3_V4_SENSITIVITY.tex',['Comparator','$\\Delta$MAE','$95\\%$ CI low','$95\\%$ CI high','Holm p'],rows)
print('3 tables')
