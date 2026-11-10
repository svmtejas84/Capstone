"""Refresh v2v provenance/checksum manifests and build its standalone ZIP."""
from pathlib import Path
import csv, hashlib, json, zipfile
from PIL import Image
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
# Figure index CSV
manifest=json.loads((P/'source_data/figure_manifest.json').read_text())
with (P/'source_data/figure_manifest.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['id','group','title','png','pdf','svg','source_data','sources'],lineterminator='\n')
    w.writeheader()
    for x in manifest:
        w.writerow({k:x.get(k,'') for k in ['id','group','title','png','pdf','svg','source_data']}|{'sources':';'.join(x.get('sources',[]))})
# Regenerate figure snippets from the final figure manifest; paths resolve from repo root.
tex=['% v2v insertion snippets only; no manuscript source is included.']
for x in manifest:
    label='fig:'+x['id'].lower().replace('_','-')
    tex += [r'\begin{figure*}[t]',r'\centering',r'\includegraphics[width=\textwidth]{final_blr_results/ieee_publication_assets_v2v/'+x['pdf']+'}',r'\caption{'+x['caption'].replace('%',r'\%')+'}',r'\label{'+label+'}',r'\end{figure*}','']
(P/'latex/figures.tex').write_text('\n'.join(tex))
# Direct source registry
sources=set()
for x in manifest: sources.update(x.get('sources',[]))
sources.update(['notebooks/production/evaluated_wind_advection.ipynb','configs/data_v2.yaml','scripts/benchmark_v2j.py','src/stpignn/data_v2.py','src/stpignn/physics_v2.py','results/loso_per_station_v2j.csv','results/loso_predictions_v2j.parquet','final_blr_results/ieee_paper_evidence/results/RECOMPUTED_V2J_BENCHMARK.csv','final_blr_results/baselines/v2m/comparisons/ensemble_metrics.csv','final_blr_results/physics_audit/physical_diagnostics/physical_metrics.csv','final_blr_results/physics_audit/ensemble_analysis/ensemble_decomposition.csv','final_blr_results/final_research_v2r/citywide/road_predictions/road_predictions_20251008T0700Z.parquet','final_blr_results/final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv','final_blr_results/final_routing_closure/v2t/ROUTING_CAPACITY_METRICS.csv','final_blr_results/final_three_pillars/captum/attribution_tensors.npz','final_blr_results/final_three_pillars/captum/v2r_heldout_h6/attribution_tensors.npz'])
source_rows=[]
for rel in sorted(sources):
    src=ROOT/rel
    source_rows.append({'path':rel,'exists':src.is_file(),'bytes':src.stat().st_size if src.is_file() else '', 'sha256':hashlib.sha256(src.read_bytes()).hexdigest() if src.is_file() else ''})
with (P/'verification/SOURCE_HASHES.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','exists','bytes','sha256'],lineterminator='\n'); w.writeheader(); w.writerows(source_rows)
missing=[r['path'] for r in source_rows if not r['exists']]
# User-facing verification findings; the script verify_package.py runs separately.
report=f'''# Publication asset verification\n\n## Executed checks\n\n- {len(manifest)} figure records (F01, F02, F03, F03b, F04, F05, F06a, F06b, F07, F08, F08b). PNG images are decoded by Pillow; PDF headers and SVG roots are checked by `verify_package.py`.\n- Direct-source register: {len(source_rows)} artifacts; {len(missing)} missing. All figure-manifest sources are checked for existence.\n- Forecast inventory: 17 saved retrospective-weather model variants (85 model-horizon rows); MLP/TCN are a separate cutoff-safe protocol (10 ensemble rows).\n- Routing reconciliation: original-field maximum 4.5918%; all four fields maximum 5.4054% in the spatial-sine perturbation.\n- Five directional-minus-Laplacian seven-day moving-block intervals, the exact 5/5 seed sign test, station-level bootstrap, and raw-tensor IG values are saved in source tables and audit reports.\n- T03b records the available corrected station-space directional-cone diagnostic. It measures prediction monotonicity, not physical conservation.\n- 11 CSV tables and LaTeX snippets are registered. Reader-facing figure/table labels use descriptive protocol/model names; internal identifiers remain in provenance CSVs.\n- Visual inspection: F01, F03, F03b, F05, F06a, F06b, and F08.\n\n## LaTeX and limits\n\nNo `pdflatex` or `latex` executable was available. Snippets are insertion-only, statically path-checked from repository root; no manuscript or manuscript PDF was produced. The older provenance registry also records one absent path, `final_blr_results/baselines/v2m/methodology/WEATHER_AVAILABILITY_AUDIT.md`; it is disclosed and not silently substituted.\n\nCenter-weather and cutoff-safe protocols remain separate. Spatial evaluation has 11 scored stations. Captum is variant-specific and baseline-relative. Citywide estimates lack independent roadside labels. Routing dose is modeled under scenarios and is not measured exposure. No conservation or classical matching-stability claim is made.\n\n### Missing direct source paths\n\n{chr(10).join('- `'+x+'`' for x in missing) if missing else 'None.'}\n'''
(P/'verification/PUBLICATION_ASSET_VERIFICATION.md').write_text(report)
# Hash all deliverable package files; exclude only self-referential checksum and the external ZIP.
archive=P/'IEEE_PUBLICATION_ASSETS_v2v.zip'
checks=[]
for f in sorted(P.rglob('*')):
    if f.is_file() and f.name not in {'CHECKSUMS.csv','IEEE_PUBLICATION_ASSETS_v2v.zip'}:
        checks.append({'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
with (P/'verification/CHECKSUMS.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n'); w.writeheader(); w.writerows(checks)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in sorted(P.rglob('*')):
        if f.is_file() and f!=archive: z.write(f,f.relative_to(P.parent))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    expected={x['path']:x['sha256'] for x in checks}
    for member in z.namelist():
        rel=Path(member).relative_to(P.name).as_posix()
        if rel in expected: assert hashlib.sha256(z.read(member)).hexdigest()==expected[rel], rel
print(f'figures={len(manifest)} tables={len(list((P/"tables").glob("T*.csv")))} sources={len(source_rows)} missing={len(missing)} files={len(checks)} zip_bytes={archive.stat().st_size} zip_sha256={hashlib.sha256(archive.read_bytes()).hexdigest()}')
