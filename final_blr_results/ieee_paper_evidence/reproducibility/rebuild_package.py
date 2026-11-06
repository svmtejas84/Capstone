from pathlib import Path
import os,subprocess,sys
root=Path('final_blr_results/ieee_paper_evidence/reproducibility')
steps=['build_tables.py','recompute_v2j_benchmark_from_archive.py','recompute_v2m_summaries_from_archive.py','recompute_v2m_primary_contrasts.py','verify_saved_metrics.py','append_spatial_tables.py','generate_figures.py','add_figures.py','graph_map.py','add_v2j_benchmark.py','annotate_figure_manifest.py','finalize_tables.py','build_manifest.py','verify_package.py']
env=os.environ.copy();env['MPLCONFIGDIR']='/tmp/stpignn_evidence_mpl'
for step in steps:
 print('RUN',step,flush=True)
 subprocess.run([sys.executable,str(root/step)],check=True,env=env)
print('EVIDENCE PACKAGE REBUILD COMPLETE',flush=True)
