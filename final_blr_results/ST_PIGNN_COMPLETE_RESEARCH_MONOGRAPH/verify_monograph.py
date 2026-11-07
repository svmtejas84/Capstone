"""Independent structural, source-hash and selected numerical checks for the monograph."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

from build_appendices import REGISTERS

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent

def digest(p: Path) -> str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''): h.update(block)
 return h.hexdigest()

def csvrows(p: Path):
 with p.open(newline='',errors='replace') as f: return list(csv.DictReader(f))

def check() -> dict:
 (BASE/'reproducibility').mkdir(exist_ok=True)
 (BASE/'reproducibility/MONOGRAPH_VERIFICATION_REPORT.md').touch(exist_ok=True)
 vols=sorted((BASE/'volumes').glob('VOLUME_*.md'))
 apps=sorted((BASE/'appendices').glob('COMPLETE_*.md'))
 assert len(vols)==16, len(vols)
 assert len(apps)==15, len(apps)
 source_rows=csvrows(BASE/'source_registry/SOURCE_COVERAGE.csv')
 bad_source=[r['source_path'] for r in source_rows if not (ROOT/r['source_path']).is_file() or digest(ROOT/r['source_path'])!=r['sha256']]
 appendix_sources={s for sources in REGISTERS.values() for s in sources}
 bad_appendix=[]
 for name,sources in REGISTERS.items():
  appendix=(BASE/'appendices'/f'{name}.md').read_text()
  for s in sources:
   if not (ROOT/s).is_file() or digest(ROOT/s) not in appendix:
    bad_appendix.append(f'{name}: {s}')
 copied=csvrows(BASE/'tables/TABLE_SOURCE_MAP.csv')
 bad_table=[r['monograph_copy'] for r in copied if not (BASE/r['monograph_copy']).is_file() or digest(BASE/r['monograph_copy'])!=r['sha256'] or digest(ROOT/r['source'])!=r['sha256']]
 figs=csvrows(BASE/'figures/FIGURE_SOURCE_MAP.csv')
 bad_fig=[r['monograph_copy'] for r in figs if not (BASE/r['monograph_copy']).is_file() or digest(BASE/r['monograph_copy'])!=r['sha256'] or digest(ROOT/r['source'])!=r['sha256']]
 assert not bad_source and not bad_appendix and not bad_table and not bad_fig, (bad_source,bad_appendix,bad_table,bad_fig)
 # Authored links only. Embedded historical reports may carry external citations.
 broken=[]
 authored=[BASE/'ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH.md',BASE/'TABLE_OF_CONTENTS.md',BASE/'README.md',BASE/'appendices/COMPLETE_ARTIFACT_INVENTORY.md']
 for p in authored:
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   target=target.split('#')[0]
   if not target or '://' in target or target.startswith('mailto:'): continue
   if not (p.parent/target).exists(): broken.append(f'{p.relative_to(BASE)} -> {target}')
 assert not broken,broken
 commit=subprocess.run(['git','cat-file','-e','1c46a4b605f2d8e8ba25a407ace756e675a8aa15^{commit}'],cwd=ROOT,check=False).returncode==0
 assert commit
 # Re-evaluate the key reported numbers from source tables without fitting a model.
 dec=csvrows(ROOT/'final_blr_results/final_research_v2r/citywide/spatial_decoder/pooled_test_metrics.csv')
 d={r['method']:float(r['mae']) for r in dec}
 assert round(d['forecast_decoder'],3)==27.360 and round(d['forecast_idw'],3)==20.154 and round(d['train_only_spatial_mean'],3)==20.634
 assert {int(r['n']) for r in dec}=={14583} and {int(r['scored_stations']) for r in dec}=={11}
 v2m=csvrows(ROOT/'final_blr_results/baselines/v2m/comparisons/primary_ten_comparisons.csv')
 favorable=[(int(r['horizon_hours']),r['baseline']) for r in v2m if r['holm_reject_0_05']=='True' and float(r['paired_mae_difference'])<0]
 assert favorable==[(6,'mlp'),(12,'mlp')],favorable
 integ=json.loads((ROOT/'final_blr_results/final_routing_closure/v2t/OUTPUT_INTEGRITY.json').read_text())
 assert integ['saved_rows']==6048 and integ['invalid_routes']==0 and integ['shared_directed_edge_capacity_violations']==0
 routing=csvrows(ROOT/'final_blr_results/final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv')
 assert len(routing)==216 and max(float(r['max_utilization']) for r in routing)<0.055
 assert all(int(r['requests'])==int(r['assigned']) for r in routing)
 orig_pdf=list(ROOT.glob('ST_PIGNN_IEEE_Big_Data_Conf(2).pdf'))
 notebook=ROOT/'notebooks/production/evaluated_wind_advection.ipynb'
 nb=json.loads(notebook.read_text())
 assert len(nb['cells'])==26 and all(c['cell_type']=='code' for c in nb['cells'])
 assert digest(notebook)=='242d0cf3d2f95c78a011841ed2aec2e100cc8c326e6211c918a8bd70504b8161'
 cells=['# Original production notebook cell map\n',f'Source `{notebook.relative_to(ROOT)}`; SHA-256 `{digest(notebook)}`. Static inspection only; no cell executed. Twenty-six code cells, no saved outputs or markdown cells.\n','| Cell | Lines | Definitions/imports (first occurrences) |','|---:|---:|---|']
 for i,c in enumerate(nb['cells']):
  s=''.join(c['source']);ls=s.splitlines()
  statements=[x.strip().replace('|','\\|') for x in ls if re.match(r'^\s*(def |class |from |import |[A-Z][A-Z0-9_]*\s*=)',x)]
  cells.append(f'| {i} | {len(ls)} | {"; ".join(statements[:6])[:350] or "No top-level definition/import in first static scan"} |')
 (BASE/'source_registry/ORIGINAL_NOTEBOOK_CELL_MAP.md').write_text('\n'.join(cells)+'\n')
 # Source coverage includes full exhibits; explicitly register directly inspected code/notebook.
 direct=[notebook,ROOT/'gnn/model.py',ROOT/'src/stpignn/data_v2.py',ROOT/'src/stpignn/station_graph.py',
         ROOT/'src/stpignn/models_v2.py',ROOT/'src/stpignn/models_v3.py',ROOT/'src/stpignn/physics_v2.py',
         ROOT/'src/stpignn/rgdr.py',ROOT/'src/stpignn/rgdr_continuous.py',ROOT/'matcher/gale_shapley.py',
         ROOT/'matcher/edge_capacity_da.py',ROOT/'router/api/routes.py',ROOT/'scripts/evaluate_routing_gs.py',
         ROOT/'final_blr_results/final_three_pillars/physics/conservation_diagnostic.py',
         ROOT/'final_blr_results/final_three_pillars/captum/run_v2c_ig.py',
         ROOT/'final_blr_results/final_three_pillars/captum/run_v2r_heldout_ig.py']
 direct_rows=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p),'bytes':p.stat().st_size,'inspection':'static source check'} for p in direct]
 with (BASE/'source_registry/DIRECT_SOURCE_CHECKS.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['path','sha256','bytes','inspection'],lineterminator='\n');w.writeheader();w.writerows(direct_rows)
 all_sources={r['source_path'] for r in source_rows}|appendix_sources|{r['source'] for r in copied}|{r['source'] for r in figs}|{str(p.relative_to(ROOT)) for p in direct}
 with (BASE/'source_registry/COMPLETE_SOURCE_COVERAGE.csv').open('w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['source_path','sha256','bytes','coverage_type'])
  for s in sorted(all_sources):
   q=ROOT/s
   kinds=[]
   if s in {r['source_path'] for r in source_rows}: kinds.append('volume exhibit')
   if s in appendix_sources: kinds.append('appendix source')
   if s in {r['source'] for r in copied}: kinds.append('copied result table')
   if s in {r['source'] for r in figs}: kinds.append('copied figure')
   if q in direct: kinds.append('direct static source')
   w.writerow([s,digest(q),q.stat().st_size,'; '.join(kinds)])
 words=sum(len(p.read_text(errors='replace').split()) for p in [BASE/'ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH.md']+vols+apps)
 equation_count=(BASE/'appendices/COMPLETE_EQUATION_REGISTER.md').read_text().count('$$')//2
 report={'volumes':len(vols),'appendices':len(apps),'master_plus_volume_appendix_words':words,
         'full_report_exhibits_unique':len(source_rows),'direct_source_checks':len(direct_rows),'distinct_source_artifacts_referenced':len(all_sources),
         'copied_numeric_tables':len(copied),'figure_files':len(figs),'figure_pairs':len(figs)//2,
         'display_equations_in_equation_register':equation_count,
         'experiment_register_rows':len(csvrows(ROOT/'final_blr_results/ieee_paper_evidence/source_registry/EXPERIMENT_SOURCE_REGISTER.csv')),
         'reachable_git_commits':sum(1 for line in (BASE/'appendices/COMPLETE_COMMIT_CHRONOLOGY.md').read_text().splitlines() if re.match(r'^\| [0-9a-f]{40} \|',line)),
         'source_hash_mismatches':bad_source,'appendix_source_mismatches':bad_appendix,'table_hash_mismatches':bad_table,'figure_hash_mismatches':bad_fig,
         'broken_authored_links':broken,'key_numeric_checks':'PASS',
         'original_notebook_cells':26,'original_notebook_sha256':digest(notebook),
         'original_manuscript_pdf_present':bool(orig_pdf),'full_review_texts_present':False,
         'unresolved_source_categories':['submitted BigData PDF','four BigData full reviews','two DELCON full reviews','original manuscript bibliography/page and figure mapping','some historical checkpoints and training state','independent roadside observations and external replication'],
         'pdf_edition':'NOT GENERATED: pandoc unavailable; authoritative Markdown complete'}
 (BASE/'reproducibility').mkdir(exist_ok=True)
 (BASE/'reproducibility/verification.json').write_text(json.dumps(report,indent=2)+'\n')
 lines=['# Monograph verification report\n','This audit checks the generated documentation and selected saved numerical evidence. It does not rerun model training or reconstruct missing external sources.\n',
        f'- Volumes: **{len(vols)}/16**; appendices: **{len(apps)}/15**; master/volume/appendix words: **{words:,}**.',
        f'- Distinct source artifacts across exhibits, appendices, tables, figures and code: **{len(all_sources)}**. Full report exhibits: **{len(source_rows)}**; direct notebook/code checks: **{len(direct_rows)}**.',
        f'- Copied numeric tables: **{len(copied)}**, all source SHA-256 matched; figures: **{len(figs)//2} PNG/PDF pairs**, all source SHA-256 matched.',
        f'- The equation register contains **{equation_count}** rendered display equations, with version/units boundaries.',
        f'- Authored internal links broken: **{len(broken)}**. Source/figure/table hash mismatches: **{len(bad_source)+len(bad_appendix)+len(bad_table)+len(bad_fig)}**.',
        f'- Experiment source-register rows: **{report["experiment_register_rows"]}**. Original notebook: **26 code cells**, SHA-256 `{digest(notebook)}`.',
        '- Rechecked v2r decoder pooled MAEs and population, v2m Holm-surviving comparisons, v2t saved-output integrity and comparison-row completeness. All assertions passed.',
        '- No conflict is silently repaired. Historical v2n handoff states corrected ST-PIGNN IG unavailable; the later three-pillar recovery added v2c and v2r h=6 checkpoint IG, not missing final v2j weights. The master and Volume 11 distinguish these versioned results.',
        '- Original submitted PDF and six full reviews remain absent. Exact paper pages/figures, quotations, reviewer assignments and original reference audit are **BLOCKED BY MISSING SOURCE**. This is a source limitation, not a completed reconciliation.',
        '- Independent street-level accuracy, real exposure reduction, RGDR predictive superiority, mass-conservation of historical checkpoints and second-city replication remain unsupported or unevaluated.',
        '- PDF edition not generated because `pandoc` was not installed; Markdown is authoritative.\n',
        '## Reproduction\n',
        '`python final_blr_results/ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH/verify_monograph.py` from the repository root. The source snapshot commit is reachable and source hashes are in `source_registry/SOURCE_COVERAGE.csv`.\n']
 (BASE/'reproducibility/MONOGRAPH_VERIFICATION_REPORT.md').write_text('\n'.join(lines))
 progress=BASE/'MONOGRAPH_PROGRESS.md'
 current=progress.read_text()
 current=current.replace(' | WRITTEN | ', ' | COMPLETE | ').replace('final consistency audit pending.', 'source hashes, authored links and key saved numerical claims cross-checked.')
 current=current.replace('Appendices are generated from saved registries and copied tables. No chapter is marked COMPLETE before source, numerical and link verification. Next: inspect generated appendices, run independent checks, document discrepancies, archive and publish.',
  'Appendices: 15/15 COMPLETE as copied source registers, subject to the same historical source limits. Volumes 3–16: COMPLETE under the available evidence. Volumes 1–2: BLOCKED BY MISSING SOURCE for the submitted PDF and six full reviews, while recoverable code/review-topic evidence is documented. Verification report records zero hash or authored-link failures and passing selected numerical checks. Next: archive and publish; source transfer can later remove the two primary-source blocks.')
 progress.write_text(current)
 return report

if __name__=='__main__': print(json.dumps(check(),indent=2))
