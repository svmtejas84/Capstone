"""Build exhaustive machine-backed registers and bounded human-readable tables."""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
AP = BASE/'appendices'
TAB = BASE/'tables'
E = 'final_blr_results/ieee_paper_evidence/'
P = 'final_blr_results/'

REGISTERS = {
 'COMPLETE_EXPERIMENT_REGISTER': [E+'source_registry/EXPERIMENT_SOURCE_REGISTER.csv', P+'city_scale/final_evidence/BENGALURU_EXPERIMENT_REGISTER.md'],
 'COMPLETE_MODEL_CONFIGURATION_REGISTER': [P+'baselines/baseline_inventory.csv', P+'physics_audit/provenance/model_configurations.csv', P+'physics_audit/selection_audit/selected_configurations.csv', P+'baselines/v2m/comparisons/selected_configurations.csv'],
 'COMPLETE_DATASET_REGISTER': [P+'city_scale/features/feature_registry.csv', P+'citywide_extension/v2o/ROAD_NODE_FEATURE_REGISTRY.csv', P+'city_scale/graph/graph_integrity.csv'],
 'COMPLETE_FEATURE_DICTIONARY': [P+'city_scale/features/feature_registry.csv', P+'citywide_extension/v2o/ROAD_NODE_FEATURE_REGISTRY.csv', P+'baselines/v2m/methodology/weather_availability_audit.csv'],
 'COMPLETE_RESULTS_REGISTER': [E+'results/MASTER_RESULTS.csv', E+'results/RECOMPUTED_V2J_BENCHMARK.csv', E+'results/RECOMPUTED_V2M_ENSEMBLE_METRICS.csv', E+'results/RECOMPUTED_V2M_PRIMARY_DELTAS.csv', P+'final_research_v2r/citywide/spatial_decoder/pooled_test_metrics.csv', P+'final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv'],
 'COMPLETE_FIGURE_REGISTER': [E+'figures/figure_manifest.csv', P+'final_three_pillars/captum/CAPTUM_FINAL_VERDICT.md'],
 'COMPLETE_REFERENCE_REGISTER': [E+'references/CITATION_ISSUES.md', E+'references/PRIOR_ART_MATRIX.md', P+'citywide_extension/v2p_rgdr/RGDR_PRIOR_ART_REVIEW.md'],
 'COMPLETE_REVIEWER_CRITICISM_MATRIX': [E+'reviewers/BIGDATA_REVIEWER_MATRIX.md', E+'reviewers/DELCON_REVIEWER_MATRIX.md', E+'reviewers/CRITICISM_RESOLUTION_SUMMARY.md'],
 'COMPLETE_CLAIM_EVIDENCE_MATRIX': [E+'claims/CLAIM_CLASSIFICATIONS.csv', P+'city_scale/final_evidence/CLAIM_EVIDENCE_MATRIX.csv', P+'final_three_pillars/CLAIM_EVIDENCE_MATRIX.csv', P+'final_routing_closure/v2t/IEEE_ROUTING_CLAIM_DECISION.md'],
 'COMPLETE_FAILURE_AND_CORRECTION_LOG': [P+'city_scale/final_evidence/KNOWN_LIMITATIONS.md', P+'final_research_v2r/FINAL_RESEARCH_HANDOFF.md', P+'final_routing_closure/original_gale_shapley_audit/ORIGINAL_ROUTING_VERDICT.md', P+'final_routing_closure/v2t/ROUTING_FINAL_VERDICT.md'],
 'COMPLETE_REPRODUCIBILITY_COMMANDS': [E+'reproducibility/REGENERATION.md', P+'final_research_v2r/reproducibility/REPRODUCIBILITY.md', P+'final_three_pillars/reproducibility/REGENERATION.md', P+'final_routing_closure/v2t/reproducibility/REGENERATION.md'],
 'COMPLETE_UNRESOLVED_ISSUES': [E+'source_registry/MANUSCRIPT_SOURCE_REGISTER.md', E+'claims/LIMITATIONS.md', P+'city_scale/final_evidence/KNOWN_LIMITATIONS.md', P+'second_city_handover/SECOND_CITY_RESEARCH_GATES.md'],
}

def digest(p: Path) -> str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''): h.update(chunk)
 return h.hexdigest()

def esc(s: str) -> str:
 return s.replace('|','\\|').replace('\n','<br>').replace('\r','')

def source_text(path: str) -> str:
 p=ROOT/path
 if not p.is_file(): raise FileNotFoundError(path)
 tag=f'[EVIDENCE: `{path}` | SHA-256 `{digest(p)}` | snapshot `1c46a4b`]'
 if p.suffix=='.csv':
  with p.open(newline='',errors='replace') as f: rows=list(csv.reader(f))
  if not rows: return tag+'\n\nEmpty source table.\n'
  out=[tag, '', f'Rows: {len(rows)-1}. Columns: {len(rows[0])}. Units, population and protocol are those declared by the source columns or its methodology.', '',
       '| '+' | '.join(esc(x) for x in rows[0])+' |', '| '+' | '.join('---' for _ in rows[0])+' |']
  for row in rows[1:]: out.append('| '+' | '.join(esc(x) for x in row)+' |')
  return '\n'.join(out)+'\n'
 return tag+'\n\n'+p.read_text(errors='replace').strip()+'\n'

EQUATIONS = r'''# Complete equation register

Equations are separated by implementation generation. `C` is physical concentration in µg/m³ unless a normalized variable is explicitly stated. Geometry, topology and source provenance govern whether an equation has a physical interpretation.

## Observed-target forecasting

For station (i), issue time (t), horizon (h), the target is observed (y_{i,t+h}) with observation mask (m_{i,t+h}=1). A 12-hour input uses only timestamps at or before (t). A masked loss is (L_{data}=\sum m_{i,t+h}\ell(\hat y_{i,t+h},y_{i,t+h})/\sum m_{i,t+h}\). Missing targets never become observed zeros. The corrected residual target uses a log1p-compatible transformation and a forecast-origin anchor; its exact scaling parameters are version-specific. [EVIDENCE: `src/stpignn/data_v2.py`; `final_blr_results/ieee_paper_evidence/methodology/TRAINING_AND_EVALUATION.md`]

## GINE and GRU

The GINE operation is of the form (x_i' = \mathrm{MLP}((1+\epsilon)x_i+\sum_{j\in N(i)}\mathrm{ReLU}(x_j+e_{ji}))\), with learned feature vectors (x_i,e_{ji}\). The recurrent update is (z_t=\sigma(W_z x_t+U_z h_{t-1}+b_z)), (r_t=\sigma(W_r x_t+U_r h_{t-1}+b_r)), (\tilde h_t=\tanh(W_h x_t+U_h(r_t\odot h_{t-1})+b_h)), (h_t=(1-z_t)\odot\tilde h_t+z_t\odot h_{t-1}\). These are standard library components; the exact block order and tensor dimensions are documented in Volume 5. [EVIDENCE: `gnn/model.py`; `src/stpignn/models_v2.py`]

## Directional hinge

The corrected upwind-inspired loss selects eligible directed edges (M_{ij,t}\in\{0,1\}\) and applies a geometric factor (g_{ij}\), schematically (L_{dir}=\sum M_{ij,t}g_{ij}[\max(0,\hat y_{j,t}-\hat y_{i,t})]^2/(\sum M_{ij,t}+\epsilon)\). Exact wind-bearing sign, normalization, predictor scale and warm-up are those in `src/stpignn/physics_v2.py` and the v2l methodology. It is a monotonicity heuristic, not a flux balance. [EVIDENCE: `final_blr_results/physics_audit/methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md`]

## Reliability gate

Binary V1 uses provenance flags from `lag_is_imputed`. Continuous V2 uses (q_i(t)=\exp[-\Delta_i(t)/\tau]\) for an eligible past observation and zero otherwise, with frozen (\tau=4\,h\), maximum lookback 24 h, (r_{ij,t}=q_i(t)q_j(t)\). The gated hinge replaces (M\) by (Mr\) while retaining the declared directional geometry and normalization. Observation age is not calibrated uncertainty. [EVIDENCE: `final_blr_results/final_research_v2r/rgdr/continuous_v2/RGDR_CONTINUOUS_V2_SPEC.md`]

## Conservation diagnostic

A finite-volume cell balance is (V_i(C_i^{n+1}-C_i^n)/\Delta t+\sum_{f\in\partial i}(F^{adv}_{f}+F^{diff}_{f})=V_i(S_i-R_i)\). Here (V_i\) is cell volume (m³), (C_i\) concentration (µg/m³), fluxes µg/h, sources/removal µg/(m³ h); flux orientation and boundary conditions must be explicit. The standalone synthetic diagnostic tests this equation; historical ST-PIGNN checkpoints do not implement it. [EVIDENCE: `final_blr_results/final_three_pillars/physics/CONSERVATION_FORMULATION.md`]

## Interpolation, modeled dose and capacity

IDW at query (q\) is (\hat C(q)=\sum_i w_i(q)\hat C_i/\sum_i w_i(q)\), with (w_i(q)=d(q,i)^{-p}\) for eligible source stations and a documented zero-distance rule. For an edge of length (L_e\) meters, constant speed (v\) m/h, RMV (R\) m³/h and concentration (C_e\) µg/m³, modeled inhaled dose is (D_e=C_eR L_e/v\) µg. For every directed edge (e\), the corrected allocation checks (\sum_{u:e\in R_u}d_{u,e}\le K_e\); one simulated commuter consumes one unit in v2t. These equations define model output, not measured exposure or actual traffic capacity. [EVIDENCE: `final_blr_results/final_routing_closure/v2t/CAPACITY_ALLOCATOR_SPECIFICATION.md`]

## Integrated Gradients

For scalar forecast (F(x)\) and baseline (x'\), (IG_k(x;x')=(x_k-x'_k)\int_0^1\partial F(x'+\alpha(x-x'))/\partial x_k\,d\alpha\). Completeness compares (\sum_k IG_k\) with (F(x)-F(x')\); numerical integration error is reported by Captum. The choice of baseline changes attribution. No causal or conservation inference follows. [EVIDENCE: `final_blr_results/final_three_pillars/captum/IG_METHODOLOGY.md`]
'''

EQUATIONS = r"""# Complete equation register

All equations identify the implementation generation or diagnostic they describe. The source files cited after each formula fix the precise tensor convention. Concentration \(C\) has units µg/m³ unless a normalized predictor is stated.

## 1. Observed-target station forecast

For station \(i\), issue time \(t\), horizon \(h\), and observed-target mask \(m_{i,t+h}\), a masked empirical loss is

$$L_{\mathrm{data}}=\frac{\sum_{i,t}m_{i,t+h}\ell(\hat y_{i,t+h},y_{i,t+h})}{\sum_{i,t}m_{i,t+h}}.$$

The 12-hour input window must end no later than issue time \(t\). A missing observation is never a measured zero. The corrected log1p-compatible residual anchor and scale are dataset-version-specific. Evidence: src/stpignn/data_v2.py; IEEE evidence training methodology.

## 2. Edge-aware GINE and temporal GRU

For latent node vector \(x_i\), encoded edge vector \(e_{ji}\), and graph neighborhood \(N(i)\):

$$x_i'=\operatorname{MLP}\!\left((1+\epsilon)x_i+\sum_{j\in N(i)}\operatorname{ReLU}(x_j+e_{ji})\right).$$

One standard recurrent formulation is

$$z_t=\sigma(W_zx_t+U_zh_{t-1}+b_z),\quad r_t=\sigma(W_rx_t+U_rh_{t-1}+b_r),$$
$$\tilde h_t=\tanh(W_hx_t+U_h(r_t\odot h_{t-1})+b_h),\quad h_t=(1-z_t)\odot\tilde h_t+z_t\odot h_{t-1}.$$

The library implementation, block order, dimensions and graph topology must be read from gnn/model.py, src/stpignn/models_v2.py or src/stpignn/models_v3.py for the corresponding model version.

## 3. Directional hinge

With eligible directed-edge mask \(M_{ij,t}\), geometric factor \(g_{ij}\), normalized forecast \(\hat y\), and denominator safeguard \(\epsilon\), the schematic regularizer is

$$L_{\mathrm{dir}}=\frac{\sum_{(i,j),t}M_{ij,t}g_{ij}[\max(0,\hat y_{j,t}-\hat y_{i,t})]^2}{\sum_{(i,j),t}M_{ij,t}+\epsilon}.$$

This is a monotonicity heuristic. The exact executed mask orientation, geometric factor, normalization and warm-up are in src/stpignn/physics_v2.py and the v2l physics methodology. It is not a mass balance.

## 4. Continuous reliability gate

For eligible past-observation age \(\Delta_i(t)\), fixed \(\tau=4\) h, and maximum lookback 24 h:

$$q_i(t)=\begin{cases}\exp[-\Delta_i(t)/\tau],&\text{eligible observation exists},\\0,&\text{otherwise},\end{cases}
\qquad r_{ij,t}=q_i(t)q_j(t).$$

The gate weights the directional loss; it does not calibrate uncertainty. Binary V1 instead uses observed/imputed provenance. Evidence: v2p and v2r RGDR specifications.

## 5. Finite-volume diagnostic

For atmospheric control volume \(V_i\) m³, concentration \(C_i\) µg/m³, time step \(\Delta t\) h, advective and diffusive face fluxes \(F_f\) µg/h, and source/removal rates \(S_i,R_i\) µg/(m³ h):

$$V_i\frac{C_i^{n+1}-C_i^n}{\Delta t}+\sum_{f\in\partial i}(F_f^{\mathrm{adv}}+F_f^{\mathrm{diff}})=V_i(S_i-R_i).$$

Synthetic tests validate this standalone discretization, not historical ST-PIGNN checkpoints. Evidence: final_three_pillars/physics/CONSERVATION_FORMULATION.md.

## 6. Station-to-road interpolation

For eligible station estimates \(\hat C_i\), query coordinate \(q\), distance \(d(q,i)\), and fixed exponent \(p\):

$$\hat C(q)=\frac{\sum_i w_i(q)\hat C_i}{\sum_i w_i(q)},\qquad w_i(q)=d(q,i)^{-p}.$$

A zero-distance rule and station-exclusion fold are required. Retrospective observed-field IDW and forecast-IDW are distinct tasks. Evidence: v2o spatial estimation method and v2r spatial methodology.

## 7. Modeled inhaled dose and edge quotas

For edge concentration \(C_e\) µg/m³, respiratory minute-volume converted to rate \(R\) m³/h, edge length \(L_e\) m and speed \(v\) m/h:

$$D_e=C_eR\frac{L_e}{v}\quad[\mu\mathrm g].$$

The corrected allocator checks every directed edge \(e\) after each proposal and at termination:

$$\sum_{u:e\in R_u}d_{u,e}\le K_e.$$

Here \(d_{u,e}=1\) simulated commuter in v2t and \(K_e\) is an assumed declared quota, not measured road capacity. Evidence: final_routing_closure/v2t/CAPACITY_ALLOCATOR_SPECIFICATION.md.

## 8. Integrated Gradients

For scalar forecast \(F(x)\), input \(x\), baseline \(x'\), and feature index \(k\):

$$IG_k(x;x')=(x_k-x'_k)\int_0^1\frac{\partial F(x'+\alpha(x-x'))}{\partial x_k}\,d\alpha.$$

Completeness compares \(\sum_k IG_k\) with \(F(x)-F(x')\); baseline choice changes attribution. This is not proof of causal atmospheric transport. Evidence: final_three_pillars/captum/IG_METHODOLOGY.md.
"""

def main():
 AP.mkdir(exist_ok=True); TAB.mkdir(exist_ok=True); (BASE/'figures').mkdir(exist_ok=True)
 for name, sources in REGISTERS.items():
  text=[f'# {name.replace("_"," ").title()}\n',
        'This register reproduces the cited source records below, retaining their original protocol and status. Later source exhibits can supersede earlier conclusions; no incompatible populations are pooled.\n']
  for i,s in enumerate(sources,1): text += [f'## Source {i}: `{s}`\n',source_text(s)]
  if name=='COMPLETE_CLAIM_EVIDENCE_MATRIX':
   text += ['## Historical-to-final claim reconciliation\n',
    '| Historical or proposed claim | Final status | Evidence and boundary |', '|---|---|---|',
    '| Original reported MAE 53.14 µg/m³ and PVR 1.404% demonstrate a reliable city forecast | HISTORICALLY INVALIDATED as a validity inference; original figures UNVERIFIABLE without PDF | v2q notebook recovery identified target-hour and duplicated-input defects; no observed road-node truth. |',
    '| The original directional hinge conserves atmospheric mass | HISTORICALLY INVALIDATED | v2l and three-pillar loss audits show no dimensioned flux/source balance; synthetic later finite-volume tests do not alter old weights. |',
    '| Corrected station ST-PIGNN dominates all neural baselines | UNSUPPORTED | v2j/v2m results vary by horizon; no TCN contrast survived the reported Holm family, and weather protocols differ. |',
    '| The compact v2r decoder improves held-out-site forecasting | UNSUPPORTED | Eleven-site matched validation: decoder MAE 27.360 versus forecast-IDW 20.154 and train-only mean 20.634 µg/m³. |',
    '| Full 154,902-node citywide estimation ran | SUPPORTED as computational execution | Three h=6 snapshots yielded 464,706 experimental neural-assisted values; road accuracy NOT EVALUATED. |',
    '| Continuous RGDR improves prediction | NOT EVALUATED | Training-only gate exposure failed frozen feasibility thresholds before the comparative pilot. |',
    '| Corrected v2t allocation respects declared shared-edge quotas | SUPPORTED within the declared simulation | Focused 20/20 tests and 6,048 saved rows with zero scanned violations; city demand did not saturate edges. |',
    '| Routing lowers measured commuter exposure | NOT EVALUATED | Static concentration and RMV/capacity assumptions, negligible modeled dose change and no measured exposure. |\n']
  (AP/(name+'.md')).write_text('\n'.join(text))
 (AP/'COMPLETE_EQUATION_REGISTER.md').write_text(EQUATIONS)
 commits=subprocess.check_output(['git','log','1c46a4b605f2d8e8ba25a407ace756e675a8aa15','--date=iso-strict','--format=%H%x09%ad%x09%s'],cwd=ROOT,text=True).splitlines()
 lines=['# Complete recoverable research-source Git commit chronology\n','This is a mechanical listing of commits reachable from frozen pre-monograph source snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15`, not a claim that every experiment has a unique training commit. Later documentation-publication commits are intentionally outside this research-source chronology. Date is the recorded Git author date, not proof of experiment execution time.\n','| Commit | Recorded date | Subject |','|---|---|---|']
 for row in commits:
  x=row.split('\t',2)
  if len(x)==3: lines.append('| '+' | '.join(esc(i) for i in x)+' |')
 (AP/'COMPLETE_COMMIT_CHRONOLOGY.md').write_text('\n'.join(lines)+'\n')
 inventory=ROOT/(P+'archive/archive_integrity.csv')
 (TAB/'v2k_archive_integrity.csv').write_bytes(inventory.read_bytes().replace(b'\r\n',b'\n'))
 lines=['# Complete artifact inventory\n',f'The v2k integrity census is included in this monograph at [`tables/v2k_archive_integrity.csv`](../tables/v2k_archive_integrity.csv): 2,141 inventoried artifacts and 318 unmatched result files at its 2026-11-05 snapshot. It is a historical census, not a claim that all later v2m–v2t files were already present. Source SHA-256: `{digest(inventory)}`; copied content differs only by CRLF-to-LF line-ending normalization.\n',
        'Later rounds are separately represented by the complete source coverage CSV, the following manifests and the copied results tables. Missing checkpoint classes and external backup remain explicitly unresolved.\n',
        '| Round | Inventory source | Status |','|---|---|---|']
 for s in [P+'baselines/v2m/reproducibility/RESEARCH_RESULTS_v2m_MANIFEST.csv',P+'city_scale/reproducibility/artifact_checksums.csv',P+'final_research_v2r/reproducibility/artifact_checksums.csv',P+'final_three_pillars/reproducibility/CHECKSUMS.csv',P+'final_routing_closure/v2t/reproducibility/checksums.csv']:
  q=ROOT/s
  if q.is_file(): lines.append(f'| {s.split("/")[1]} | `{s}` | present; SHA-256 `{digest(q)}` |')
 (AP/'COMPLETE_ARTIFACT_INVENTORY.md').write_text('\n'.join(lines)+'\n')
 # Copy authoritative machine-readable tables without changing values.
 copied=[]
 for p in sorted((ROOT/(E+'results')).glob('*.csv')):
  dest=TAB/p.name; shutil.copyfile(p,dest); copied.append((str(p.relative_to(ROOT)),str(dest.relative_to(BASE)),digest(dest)))
 for p in [ROOT/(P+'final_routing_closure/v2t/ROUTING_COMPARISON_RESULTS.csv'),ROOT/(P+'final_routing_closure/v2t/PAIRED_COMPARISONS.csv'),ROOT/(P+'final_routing_closure/v2t/ROUTING_CAPACITY_METRICS.csv'),ROOT/(P+'final_routing_closure/v2t/ROUTING_SENSITIVITY_RESULTS.csv')]:
  dest=TAB/('V2T_'+p.name); shutil.copyfile(p,dest); copied.append((str(p.relative_to(ROOT)),str(dest.relative_to(BASE)),digest(dest)))
 with (TAB/'TABLE_SOURCE_MAP.csv').open('w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['source','monograph_copy','sha256']);w.writerows(copied)
 figure_sources=[]
 for p in sorted((ROOT/(E+'figures/export')).glob('*')):
  if p.suffix not in {'.png','.pdf'}: continue
  dest=BASE/'figures'/p.name;shutil.copyfile(p,dest)
  figure_sources.append((str(p.relative_to(ROOT)),str(dest.relative_to(BASE)),digest(dest)))
 with (BASE/'figures'/'FIGURE_SOURCE_MAP.csv').open('w',newline='') as f:
  w=csv.writer(f,lineterminator='\n');w.writerow(['source','monograph_copy','sha256']);w.writerows(figure_sources)
 shutil.copyfile(ROOT/(E+'references/VERIFIED_REFERENCES.bib'),BASE/'source_registry'/'VERIFIED_REFERENCES.bib')
 (BASE/'source_registry'/'SOURCE_TRANSFER_REQUEST.md').write_text(
  '# Missing primary sources for original-paper and review reconstruction\n\n'
  'Please place `ST_PIGNN_IEEE_Big_Data_Conf(2).pdf` and the four IEEE BigData 2026 plus two IEEE DELCON 2026 full review texts in the repository and provide their exact paths. The current repository does not contain a verified copy. Until then, ten-page manuscript contents, exact quotations, reviewer attribution, original references and page/figure mapping are BLOCKED BY MISSING SOURCE. Adjacent drafts are not substitutes. This source gap does not block documentation of notebook code and later experiments.\n')
 toc=BASE/'TABLE_OF_CONTENTS.md'
 t=toc.read_text().split('\n## Appendices\n',1)[0]
 t+='\n## Appendices\n\n'
 for p in sorted(AP.glob('*.md')): t+=f'- [{p.stem.replace("_"," ").title()}](appendices/{p.name})\n'
 t+='\n## Source data and figures\n\n- [Table source map](tables/TABLE_SOURCE_MAP.csv)\n- [Figure source map](figures/FIGURE_SOURCE_MAP.csv)\n- [Missing-source transfer request](source_registry/SOURCE_TRANSFER_REQUEST.md)\n'
 toc.write_text(t)
 print(json.dumps({'appendices':len(list(AP.glob('*.md'))),'table_copies':len(copied),'figure_files':len(figure_sources),'reachable_commits':len(commits)},indent=2))

if __name__=='__main__': main()
