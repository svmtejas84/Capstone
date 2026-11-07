"""Assemble a source-traced ST-PIGNN research monograph from frozen reports.

This documentation builder reads historical files. It does not run experiments.
The explicit editorial introductions are interpretations; the following source
exhibits preserve the primary round-specific wording and numerical context.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
SNAPSHOT = "1c46a4b605f2d8e8ba25a407ace756e675a8aa15"
P = "final_blr_results/"
E = P + "ieee_paper_evidence/"
F = P + "final_three_pillars/"
R = P + "final_routing_closure/"
V = P + "final_research_v2r/"
O = P + "citywide_extension/"

# The volume is the substantive unit: an editorial reconstruction followed by
# full source exhibits, not a pointer to an unwritten external explanation.
VOLUMES = [
 ("01_ORIGINS_AND_ORIGINAL_PAPER", "Origins and the recoverable original paper", [
  E+"source_registry/MANUSCRIPT_SOURCE_REGISTER.md", O+"v2q/ORIGINAL_NOTEBOOK_RECOVERY.md",
  O+"v2q/ORIGINAL_MODEL_ARCHITECTURE.md", O+"v2q/ORIGINAL_NOTEBOOK_DEPENDENCY_MAP.md",
  O+"v2q/ORIGINAL_VS_CORRECTED_COMPARISON.md", "results/MANIFEST.md"]),
 ("02_REJECTION_AND_RESEARCH_RECONSTRUCTION", "Rejections and methodological reconstruction", [
  E+"reviewers/BIGDATA_REVIEWER_MATRIX.md", E+"reviewers/DELCON_REVIEWER_MATRIX.md",
  E+"reviewers/CRITICISM_RESOLUTION_SUMMARY.md", E+"source_registry/CHRONOLOGY.md",
  P+"archive/historical_results_register.md"]),
 ("03_DATA_ENGINEERING", "Data acquisition, alignment and version genealogy", [
  E+"methodology/DATA_AND_PREPROCESSING.md", "data/processed/gapfill/station_timeseries_imputation_build_report.md",
  "results/old_filtering_audit.md", "results/weather_timestamp_check_v2i.md",
  P+"baselines/v2m/methodology/weather_availability_audit.md",
  P+"city_scale/features/feature_provenance.md", P+"city_scale/features/feature_validation.md",
  P+"road_graph/road_graph_features.md", O+"v2o/ROAD_NODE_FEATURE_PROVENANCE.md"]),
 ("04_GRAPH_ENGINEERING", "Road, partition and station graphs", [
  P+"road_graph/road_graph_integrity.md", P+"road_graph/full_graph_compatibility.md",
  P+"city_scale/graph/graph_provenance.md", P+"city_scale/graph/graph_compatibility.md",
  E+"methodology/GRAPH_CONSTRUCTION.md"]),
 ("05_MODEL_ARCHITECTURE", "Original and corrected GINE–GRU architectures", [
  O+"v2q/ORIGINAL_MODEL_ARCHITECTURE.md", O+"v2q/ORIGINAL_VS_CORRECTED_COMPARISON.md",
  E+"methodology/MODEL_ARCHITECTURE.md", E+"methodology/TRAINING_AND_EVALUATION.md",
  P+"baselines/v2m/methodology/BASELINE_BENCHMARK_METHODOLOGY.md"]),
 ("06_PHYSICS_AND_TRANSPORT", "Directional penalties, attribution and conservation", [
  P+"physics_audit/methodology/PHYSICS_ATTRIBUTION_METHODOLOGY.md",
  P+"physics_audit/FINAL_PHYSICS_VERDICT.md", F+"physics/ORIGINAL_LOSS_AUDIT.md",
  F+"physics/CONSERVATION_FORMULATION.md", F+"physics/NUMERICAL_TEST_RESULTS.md",
  F+"physics/PHYSICS_FINAL_VERDICT.md"]),
 ("07_EXPERIMENTAL_CHRONOLOGY", "Experimental chronology from W series to v2t", [
  "claude_paper.md", E+"source_registry/CHRONOLOGY.md", P+"archive/historical_results_register.md",
  P+"city_scale/final_evidence/BENGALURU_EXPERIMENT_REGISTER.md", P+"FINAL_HANDOFF.md",
  O+"FINAL_EXTENSION_HANDOFF.md", V+"FINAL_RESEARCH_HANDOFF.md",
  F+"FINAL_THREE_PILLARS_HANDOFF.md", R+"v2t/FINAL_V2T_HANDOFF.md"]),
 ("08_FORECASTING_RESULTS", "Forecasting benchmarks, controls and statistical inference", [
  "results/benchmark_v2j.md", P+"baselines/v2m/FINAL_BASELINE_VERDICT.md",
  P+"physics_audit/FINAL_PHYSICS_VERDICT.md", E+"results/RESULTS_VERIFICATION.md",
  E+"methodology/TRAINING_AND_EVALUATION.md"]),
 ("09_SPATIAL_GENERALIZATION", "Station isolation and spatial controls", [
  P+"city_scale/spatial_validation/SPATIAL_VALIDATION_VERDICT.md",
  O+"v2o/SPATIAL_VALIDATION_VERDICT.md", O+"v2o/SPATIAL_ESTIMATION_METHOD.md",
  V+"citywide/spatial_validation/SPATIAL_VALIDATION_VERDICT.md",
  E+"methodology/SPATIAL_VALIDATION.md"]),
 ("10_CITYWIDE_ESTIMATION", "Compatibility, interpolation and neural-assisted road estimates", [
  P+"city_scale/inference/INFERENCE_VERDICT.md", O+"v2o/CITYWIDE_METHODOLOGY.md",
  O+"v2o/CITYWIDE_EXECUTION_RESULTS.md", O+"v2o/CITYWIDE_UNCERTAINTY_AND_SUPPORT.md",
  O+"v2q/CITYWIDE_NEURAL_VERDICT.md", V+"citywide/methodology/CITYWIDE_METHODOLOGY.md",
  V+"citywide/CITYWIDE_FINAL_VERDICT.md", E+"methodology/CITYWIDE_ESTIMATION.md"]),
 ("11_EXPLAINABILITY", "Original and corrected Integrated Gradients", [
  P+"city_scale/explainability/CAPTUM_IG_METHODOLOGY.md",
  P+"city_scale/explainability/CAPTUM_IG_RESULTS.md", F+"captum/CHECKPOINT_RECOVERY.md",
  F+"captum/IG_METHODOLOGY.md", F+"captum/CAPTUM_FINAL_VERDICT.md",
  E+"methodology/EXPLAINABILITY.md"]),
 ("12_RGDR", "Binary and continuous reliability-gated regularization", [
  O+"v2p_rgdr/RGDR_RESEARCH_HYPOTHESIS.md", O+"v2p_rgdr/RGDR_MATHEMATICAL_SPECIFICATION.md",
  O+"v2p_rgdr/RGDR_RELIABILITY_PROVENANCE.md", O+"v2p_rgdr/RGDR_PRIOR_ART_REVIEW.md",
  O+"v2p_rgdr/RGDR_VALIDATION_ONLY_RESULTS.md", V+"rgdr/continuous_v2/RGDR_CONTINUOUS_V2_SPEC.md",
  V+"rgdr/gate_diagnostics/RGDR_GATE_DIAGNOSTICS.md", V+"rgdr/RGDR_FINAL_VERDICT.md"]),
 ("13_EXPOSURE_AND_ROUTING", "Dose-aware routes and constrained preference allocation", [
  F+"routing/ROUTING_IMPLEMENTATION.md", R+"original_gale_shapley_audit/GALE_SHAPLEY_IMPLEMENTATION.md",
  R+"original_gale_shapley_audit/MATCHING_MATHEMATICAL_FORMULATION.md",
  R+"original_gale_shapley_audit/CAPACITY_AND_OVERLAP_AUDIT.md",
  R+"original_gale_shapley_audit/PREVIOUS_BENCHMARK_RECONCILIATION.md",
  R+"v2t/ROUTING_PROTOCOL.md", R+"v2t/CAPACITY_ALLOCATOR_SPECIFICATION.md",
  R+"v2t/ROUTING_CORRECTNESS_TESTS.md", R+"v2t/ROUTING_METHODOLOGY.md",
  R+"v2t/MATCHING_GUARANTEES.md", R+"v2t/ROUTING_FINAL_VERDICT.md"]),
 ("14_ENGINEERING_AND_REPRODUCIBILITY", "Execution, artifacts, backup and recovery", [
  P+"archive/reproducibility_status.md", P+"reproducibility/execution_readiness.md",
  P+"city_scale/reproducibility/regeneration_instructions.md",
  P+"baselines/v2m/reproducibility/regeneration_instructions.md",
  V+"reproducibility/REPRODUCIBILITY.md", F+"reproducibility/REGENERATION.md",
  R+"v2t/reproducibility/REGENERATION.md", E+"reproducibility/REGENERATION.md"]),
 ("15_SCIENTIFIC_ACCOUNTABILITY", "Claim boundaries, negative results and novelty", [
  E+"claims/SUPPORTED_CLAIMS.md", E+"claims/UNSUPPORTED_CLAIMS.md",
  E+"claims/NOVELTY_BOUNDARIES.md", E+"claims/LIMITATIONS.md",
  P+"city_scale/final_evidence/KNOWN_LIMITATIONS.md",
  P+"city_scale/final_evidence/FINAL_BENGALURU_RESEARCH_VERDICT.md",
  R+"v2t/IEEE_ROUTING_CLAIM_DECISION.md"]),
 ("16_FINAL_SYNTHESIS", "Original vision, realized system and future gates", [
  E+"FINAL_PAPER_EVIDENCE_HANDOFF.md", V+"FINAL_RESEARCH_HANDOFF.md",
  F+"FINAL_THREE_PILLARS_HANDOFF.md", R+"v2t/FINAL_V2T_HANDOFF.md",
  P+"second_city_handover/BENGALURU_LESSONS_AND_FAILURES.md",
  P+"second_city_handover/SECOND_CITY_RESEARCH_GATES.md"]),
]

FRAMES = {
"01": """The earliest recoverable implementation is the production notebook and its imported `gnn/model.py`, not the unavailable submitted PDF. The paper's title and selected numerical claims are supplied by the author, but its ten pages, exact figures, captions, equations and references cannot be verified. Historical claims of MAE 53.14 µg/m³ for ST-PIGNN, 75.35 for GCN, 62.51 for GRU-GCN and PVR 1.404% must therefore remain historical assertions until the PDF and its source table are transferred. The notebook is a different sort of evidence: it establishes what code existed, including 64 road partitions, a 16-channel GINE–GRU, a direct normalized output and a legacy directional hinge. It cannot establish that the submitted prose accurately represented those operations. The recovered old checkpoint strictly loads, but target-hour input, duplicated pollutant channels, modulo timeline lookup and sparse station supervision invalidate an observed-only, issue-time-safe full-road accuracy interpretation. The corrected station model is a later, distinct experiment. [EVIDENCE: v2q recovery | final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md | repository snapshot 1c46a4b]""",
"02": """Four BigData and two DELCON review texts were described by the author, but none is present as a verified file. Thus the issue matrices below are topic-level reconciliation, not complete reviewer quotations or per-reviewer attribution. The scientific response was a sequence of data audits, observed-target rebuilding, corrected chronological evaluation, stronger controls, physics attribution, spatial holdouts and routing validation. In particular, the project stopped equating city graph construction with road-level prediction accuracy, and stopped equating a directional hinge with conservation. The primary review source is needed before declaring every criticism reconciled. [EVIDENCE: source register | final_blr_results/ieee_paper_evidence/source_registry/MANUSCRIPT_SOURCE_REGISTER.md | snapshot 1c46a4b]""",
"03": """The central data distinction is observation versus imputation versus model estimate. The old gapfill layer materialized 1,073,807 pollutant rows, 777,350 of them imputed; PM2.5 specifically included 55,307 observed rows, 9,609 temporal-linear imputations and 239,734 climatology imputations. That is historical derived-layer provenance, not the corrected observed-target population. The old filtering audit found full-timeline bidirectional interpolation and climatology fits, plus an undocumented saved `y_clean` rule; these operations cannot be assumed forecast-safe. Fifteen monitoring sites provide actual PM2.5 supervision in corrected forecasting. A road coordinate is not a PM2.5 sensor. Later feature sets retained missingness provenance and observed-target masks; target-derived features at a held-out station were excluded in spatial folds. The v2i/v2j timestamp audit identified local-weather-to-UTC alignment; v2j used corrected timestamp pairing, while v2m's forecast-cutoff weather aggregation further changed input availability. Thus model rows from those rounds are exploratory cross-protocol comparisons. The original notebook's synthetic northing-derived elevation is not measured terrain. The source exhibits below document what each stage actually stored; absent exact provider versions, licenses or raw-source completeness remain unresolved rather than inferred. [EVIDENCE: historical gapfill | data/processed/gapfill/station_timeseries_imputation_build_report.md; results/old_filtering_audit.md | snapshot 1c46a4b]""",
"04": """Two graph objects must never be conflated. The road network has 154,902 nodes, 393,089 raw directed edge rows and 424,550 processed message arcs. The corrected forecasting graph has 15 observed station nodes and 60 directed kNN edges. The 64 geographical road partitions omit 7,134 cross-partition arcs, so a partition forward pass is not automatically equivalent to whole-graph message passing. The larger processed arc count follows reverse-arc construction and deduplication after self-loop handling, not extra monitors. Structural integrity supports graph engineering; it supplies no road-node label or independent roadside accuracy. [EVIDENCE: v2k road audit | final_blr_results/road_graph/road_graph_integrity.md | snapshot 1c46a4b]""",
"05": """The original `gnn/model.py` implementation applies 16→96 node encoding, two residual edge-aware GINE blocks at each of 12 hours, a 96-unit GRU and a scalar direct output; the recovered checkpoint has 98,497 parameters. Its 16 features include five duplicated pollutant channels. Corrected experiments instead use an 18-channel 12-hour station sequence with log1p-compatible residual forecasting and a 15-node graph; a v2l comparison reports a common 43,393-parameter backbone. The same tensor shape would not prove transfer between these feature/edge semantics. MLP and TCN v2m baselines used a later weather availability protocol, so their test contrasts are not identical-information architecture ablations. [EVIDENCE: original architecture | final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md | snapshot 1c46a4b]""",
"06": """The implemented upwind-inspired term penalizes a selected directed difference with a squared hinge after bearing/wind masking and geometric scaling. It encourages a local monotonic order under that mask; it does not close a control-volume mass balance, represent the full advection–diffusion PDE or supply a dimensioned emissions source Q. The v2l matched five-seed ensemble shows negative physics-minus-λ0 MAE at 3, 6 and 12 hours, but a positive point difference at 24 hours; Laplacian comparisons do not establish physical specificity. A later standalone finite-volume diagnostic passed synthetic conservation cases, which validates its numerical discretization only. It does not change historical checkpoint physics. [EVIDENCE: v2l verdict | final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md | snapshot 1c46a4b]""",
"07": """The chronology must be read as a series of changing protocols rather than a single uninterrupted benchmark. The executable evidence ledger records an initial W1 stop after a repaired one-hour AR-with-lag baseline scored 11.894 versus persistence 8.116 µg/m³. W2 later evaluated five horizons and model families; model A/B cleared the original fixed rule at selected horizons, while the proposed advection–diffusion-source model C did not clear its physics-in-architecture criterion. W6 LOSO had no neural WIN. W7 found only a weak h=6 λ=0.06 hit among five horizons, not stable across larger λ. W3 terrain had h=1 but not h=24 all-control evidence; W4 low-density experiments had negative mean R²; conformal interval coverage missed its nominal gate; W8 city input coverage blocked full-road inference. Corrected v2j re-aligned weather timestamps and preserved negative spatial findings. v2k audited graph and architecture comparisons; v2l attributed physics effects; v2m trained MLP/TCN under later weather availability; v2n blocked direct road inference; v2o built retrospective IDW surfaces; v2p defined RGDR; v2q recovered the notebook; v2r produced station/decoder folds and experimental road estimates; the three-pillar study recovered Captum/finite-volume/routing evidence; v2t corrected serving allocation. The executable ledger is embedded in full below with dates, commits, configs, seeds, tables and stop decisions. Later verdicts supersede early handoff statements where they disagree. [EVIDENCE: executable evidence ledger | claude_paper.md | snapshot 1c46a4b]""",
"08": """Evaluation populations and weather protocols are part of every result. The v2l physics comparison uses 14,583 matched observed station-hour pairs over 177 UTC days at each horizon and five seeds; paired statistics were clustered by day, with exploratory Holm families and seven-day block sensitivity. A negative MAE difference favors the first model. At h=6 the physics-minus-λ0 ensemble difference is −0.410 µg/m³; h=24 is +0.145. The v2m 50-cell MLP/TCN study found two ST-PIGNN-versus-MLP Holm-surviving contrasts at 6 and 12 hours, none versus TCN, under differing weather protocols. Strong statistical baselines and negative R² values remain part of the record. Repeated test exposure prevents confirmatory interpretation. [EVIDENCE: v2l verdict | final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md | snapshot 1c46a4b]""",
"09": """Spatial generalization is tested by holding out an entire station, not by counting many hours at that site as independent locations. Corrected W6 LOSO scored 11 stations (four had no eligible test targets): ST-PIGNN MAE 22.314 versus weather/static ridge 20.624 µg/m³. In v2r, forecast-IDW and training-only spatial mean outperformed the frozen compact decoder: 20.154 and 20.634 versus 27.360 µg/m³ over 14,583 common pairs, with decoder worse at nine of eleven scored stations. Retrospective same-hour IDW is a different task from a six-hour forecast assembled from station predictions. These unfavorable controls are evidence against spatial-transfer superiority on this exposed dataset. [EVIDENCE: v2r handoff | final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md | snapshot 1c46a4b]""",
"10": """v2n correctly blocked direct corrected-ST-PIGNN inference on road nodes: missing road time series, incompatible graph/edge semantics and absent matching v2j weights. v2o then built retrospective station-to-road IDW estimates, which are not six-hour forecasts. v2q found a historical road-partition model but its input construction was not issue-time-safe. v2r used corrected h=6 station forecasts and a frozen 1,249-parameter spatial decoder to populate all 154,902 road nodes at three preselected times: 464,706 experimental neural-assisted values. The decoder's held-out-site deficit makes the maps computational demonstrations, not validated roadside concentrations. Median nearest-station distance was 3.315 km; 19.45% of nodes were >5 km from a monitor and 60.58% outside the station convex hull. [EVIDENCE: v2r handoff | final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md | snapshot 1c46a4b]""",
"11": """Integrated Gradients attributes a scalar prediction difference relative to a chosen baseline; it cannot establish causal atmospheric transport. v2n explained available MLP/TCN checkpoints, with 85 of 228 completeness records flagged. Later recovery found five v2c h=1 corrected variants and three v2r h=6 outer-LOSO checkpoint folds, producing 54 and 18 additional IG records respectively. The latter are not the missing final v2j/λ0/Laplacian weights. Wrapper prediction equivalence and completeness were checked separately; feature, time, station and neighbor summaries must remain version-tagged. The original synthetic-elevation attribution has no validated terrain interpretation. [EVIDENCE: three-pillar Captum verdict | final_blr_results/final_three_pillars/captum/CAPTUM_FINAL_VERDICT.md | snapshot 1c46a4b]""",
"12": """RGDR was a falsifiable attempt to weight the directional penalty by input reliability after mixed physics effects. Binary V1 used imputation flags and retained only about 2.3% of train directional edges. Continuous V2 used past-observation age, q=exp(−age/4h) for eligible ages 0–24h and r=q_source q_target, but still retained 2.48% of directional edge mass and had 74.75% zero-penalty hours. It failed prespecified exposure gates; no comparative forecast pilot ran. Unit tests support implementation properties, not predictive advantage, calibrated reliability, novelty or conservation. The prior-art review finds close quality-aware and adaptive-weighting ideas, leaving originality unsettled. [EVIDENCE: v2r handoff | final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md | snapshot 1c46a4b]""",
"13": """The original serving matcher and offline evaluator are distinct. The serving API used route quotas and a forced fallback; it did not represent shared road-edge capacities. The offline evaluator reserved directed edges and generated the earlier 1,000-request report: 444 assigned, admitted-only modeled dose +0.1211%, travel time +0.1463%. v2t retained the historical implementations and added a preference-based deferred-acceptance allocator with directed-edge reservations, atomic route release and explicit UNASSIGNED. Twenty focused tests passed, and 6,048 method-request outputs contained no invalid path or declared-capacity violation. In the 1,008-request scenario the original and corrected serving paths were identical and max edge utilization only 5.405%; dose changed −0.001207% versus shortest, time +0.001324%. This is not evidence of measured human exposure reduction, universal matching stability or operational traffic capacity. [EVIDENCE: v2t verdict | final_blr_results/final_routing_closure/v2t/ROUTING_FINAL_VERDICT.md | snapshot 1c46a4b]""",
"14": """The repository uses versioned data arrays and Parquet/CSV predictions, checkpoint state dictionaries, per-round manifests, frozen protocols, SHA-256 inventories and a supervised shell runner with locks, attempt logs and completion markers. Long-running jobs were recoverable only when their own outputs and markers survived; a Codex or JupyterHub session alone was not a process supervisor. Some older optimizer/RNG states and final v2j weights were never archived. Prior local ZIPs were checksum-verified, but an independent USB copy is unverified. Reproducibility must be stated per artifact: a saved prediction summary can be independently recomputed without implying full model retraining is possible. [EVIDENCE: v2k handoff | final_blr_results/FINAL_HANDOFF.md | snapshot 1c46a4b]""",
"15": """The final claims must separate implemented code, verified numerical behavior and empirical validity. Multi-horizon station prediction and road-graph structural integrity are supported within their stated populations. Directional regularization is mixed and lacks physical specificity. Spatial decoder improvement, road-node accuracy, measured exposure benefit, mass conservation and RGDR predictive advantage are unsupported or unevaluated. The final v2t correction supports declared-capacity software feasibility only. Negative results are not ancillary: they determine what future paper claims must be withdrawn or narrowed. The bibliography and reviewer-specific claims remain source-limited until the missing PDF/review texts are supplied. [EVIDENCE: claims register | final_blr_results/ieee_paper_evidence/claims/CLAIM_CLASSIFICATIONS.csv | snapshot 1c46a4b]""",
"16": """The original vision joined sparse-monitor prediction, physics-guided urban concentration fields and safer route allocation. The completed system is narrower: exploratory corrected station forecasting; structurally valid road data; neural-assisted city maps with unfavorable station holdout evidence; numerical but nonempirical conservation diagnostics; version-specific descriptive IG; software-feasible directed-edge allocation; and an RGDR hypothesis stopped by sparse training exposure. The defensible contributions are engineering reconstruction, explicit leakage/protocol correction, unusually complete negative controls and bounded computational demonstrations. Independent roadside sensing, a genuinely new city, calibrated weather/emissions/traffic inputs and prospective validation would be needed for broader physical or public-health claims. These are future gates, not completed experiments. [EVIDENCE: v2r and v2t final handoffs | final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md; final_blr_results/final_routing_closure/v2t/FINAL_V2T_HANDOFF.md | snapshot 1c46a4b]""",
}

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()

def downshift(text: str) -> str:
    return re.sub(r'(?m)^(#{1,5}) ', lambda m: '#' * min(len(m.group(1))+2, 6) + ' ', text)

def exhibit(path: str, index: int) -> str:
    file = ROOT / path
    if not file.is_file():
        raise FileNotFoundError(path)
    content = file.read_text(errors='replace').strip()
    return (f'## Source exhibit {index}: `{path}`\n\n'
            f'[EVIDENCE: `{path}` | SHA-256 `{sha(file)}` | snapshot `{SNAPSHOT}`]\n\n'
            f'{downshift(content)}\n')

def main() -> None:
    (BASE/'volumes').mkdir(parents=True, exist_ok=True)
    (BASE/'appendices').mkdir(exist_ok=True)
    (BASE/'source_registry').mkdir(exist_ok=True)
    coverage = {}
    toc = ['# Complete research monograph — contents\n', 'The Markdown edition is authoritative. Volume introductions reconcile source exhibits; where an exhibit predates later evidence, the later verdict governs.\n']
    for code, title, paths in VOLUMES:
        p = BASE/'volumes'/f'VOLUME_{code}.md'
        lead = code[:2]
        body = [f'# Volume {int(lead)} — {title}\n', f'<a id="volume-{lead}"></a>\n',
                '## Editorial reconstruction and evidentiary boundary\n', FRAMES[lead]+'\n',
                '## Full round-specific source exhibits\n',
                'The exhibits reproduce the cited local reports as source evidence. Their original round-specific conclusions may be narrower than later findings; read the editorial reconstruction and final synthesis before treating one exhibit as the final verdict.\n']
        for i, source in enumerate(paths, 1):
            body.append(exhibit(source, i))
            coverage.setdefault(source, set()).add(code)
        p.write_text('\n'.join(body))
        toc.append(f'- [Volume {int(lead)}: {title}](volumes/VOLUME_{code}.md) — {len(paths)} source exhibits')
    (BASE/'TABLE_OF_CONTENTS.md').write_text('\n'.join(toc)+'\n')
    with (BASE/'source_registry'/'SOURCE_COVERAGE.csv').open('w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['source_path','sha256','bytes','embedded_in_volumes','source_status'])
        for source, vols in sorted(coverage.items()):
            q = ROOT/source
            w.writerow([source,sha(q),q.stat().st_size,';'.join(sorted(vols)),'FULL TEXT EMBEDDED; editorial checks separate'])
    master = ['# ST-PIGNN — complete recoverable research monograph\n',
      '## Scope, source hierarchy and reading method\n',
      'This is a technical record of the completed Bengaluru research, from the earliest recoverable notebook to the v2t routing correction. It is not the rejected IEEE manuscript or a replacement manuscript. The sixteen volumes reproduce full round-specific reports as exhibits and add an editorial interpretation. Round-specific results retain their original dataset, population and protocol. A later verdict may supersede an earlier handoff without erasing it. The Markdown source is authoritative. All numerical claims below are tied to a source exhibit or copied result table.\n',
      'The original ten-page IEEE BigData PDF and six complete BigData/DELCON review texts are missing from this repository. Consequently, no page-by-page paper reconstruction, exact reviewer quote, original citation audit or reviewer attribution is asserted. The author-supplied original title and selected numerical claims are preserved as **historical, not independently verified**. The production notebook, code and saved experiments are different sources and establish what was implemented or evaluated within their own limits. See [Volume 1](volumes/VOLUME_01_ORIGINS_AND_ORIGINAL_PAPER.md), [Volume 2](volumes/VOLUME_02_REJECTION_AND_RESEARCH_RECONSTRUCTION.md) and the [source register](source_registry/SOURCE_COVERAGE.csv).\n',
      '## The research trajectory\n',
      'The project sought to turn sparse Bengaluru PM2.5 monitoring into temporally useful estimates and lower-dose commuter routes. The original system assembled OpenStreetMap road geometry, sparse station measurements, weather fields, a road-partition GINE–GRU, a wind-aligned hinge, interpolation, Integrated Gradients and route matching. Subsequent audits showed that this integrated vision had several independent evidentiary gaps: target-hour input in the historical notebook, incomplete road-node supervision, mismatched feature and graph semantics, weak physical specificity, unfavorable station holdouts and an unvalidated pollution field for routing. Later rounds corrected forecast evaluation and made negative controls explicit. No later engineering success erases an earlier validity defect. [EVIDENCE: `final_blr_results/citywide_extension/v2q/ORIGINAL_MODEL_ARCHITECTURE.md`; `final_blr_results/FINAL_HANDOFF.md`; `final_blr_results/final_routing_closure/v2t/ROUTING_FINAL_VERDICT.md` | snapshot `1c46a4b`]\n',
      'The authoritative station forecast task uses a **15-monitor, 60-directed-edge kNN graph** and observed monitoring-station targets at 1, 3, 6, 12 and 24 hours. The canonical road graph instead contains **154,902 nodes**, **393,089 raw directed rows** and **424,550 processed message arcs**; its 64 historical partitions omit **7,134 cross-boundary arcs**. The road network passed structural integrity checks, but road nodes do not become PM2.5 monitors. The original road-partition checkpoint and corrected station checkpoint protocols differ. v2n blocked direct road-node ST-PIGNN inference for missing features, incompatible edge semantics and absent matching weights. [EVIDENCE: `final_blr_results/road_graph/road_graph_integrity.md`; `final_blr_results/city_scale/inference/INFERENCE_VERDICT.md` | snapshot `1c46a4b`]\n',
      'Corrected v2j and subsequent v2l reanalysis made the forecasting and regularization claims narrower. The directional penalty has exploratory h=3/6/12 ensemble benefits relative to λ=0 on a matched 14,583-pair station population, but h=24 is unfavorable by point estimate and generic Laplacian controls sometimes match or beat it. Its hinge is not mass conservation. v2m completed 50 MLP/TCN model-seed cells; two ST-PIGNN-versus-MLP contrasts at h=6/12 survived the stated Holm correction, none versus TCN. Historical ST-PIGNN weather inputs differed from the v2m cutoff-safe protocol, so these are not identical-information architectural ablations. The Bengaluru test data had already been examined repeatedly. [EVIDENCE: `final_blr_results/physics_audit/FINAL_PHYSICS_VERDICT.md`; `final_blr_results/baselines/v2m/FINAL_BASELINE_VERDICT.md` | snapshot `1c46a4b`]\n',
      'Spatial isolation gave unfavorable results. Corrected W6 LOSO scored eleven stations, with four unscored for lack of test targets; ST-PIGNN MAE was **22.314** versus weather/static ridge **20.624 µg/m³**. In v2r, the frozen compact decoder scored **27.360**, forecast-IDW **20.154**, and training-only mean **20.634 µg/m³** on 14,583 common station-time pairs. The decoder lost to each control at nine of eleven sites. Yet the safe station-forecast plus decoder pipeline populated all 154,902 road nodes at three frozen h=6 times, generating 464,706 finite **experimental neural-assisted estimates**. That is computational coverage, not independently validated roadside accuracy. The median nearest-monitor distance was 3.315 km and 60.58% of nodes lay outside the station convex hull. [EVIDENCE: `final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md` | snapshot `1c46a4b`]\n',
      'Later work separated explanatory and physical diagnostics. v2n Captum covered MLP/TCN models but flagged 85/228 completeness records. A three-pillar recovery attributed 54 v2c h=1 records and 18 v2r h=6 held-out-fold records after wrapper checks; these checkpoint families are not final v2j replacements. A standalone finite-volume diagnostic passed synthetic conservation tests, but historical ST-PIGNN losses and checkpoints remained nonconserving. Binary RGDR retained about 2.3% of training directional edges; continuous observation-age RGDR retained 2.48% edge mass and had 74.75% zero-penalty hours, failing its frozen feasibility gate before comparative training. Predictive RGDR advantage and methodological novelty are not established. [EVIDENCE: `final_blr_results/final_three_pillars/FINAL_THREE_PILLARS_HANDOFF.md`; `final_blr_results/final_research_v2r/FINAL_RESEARCH_HANDOFF.md` | snapshot `1c46a4b`]\n',
      'The original serving Gale–Shapley matcher used route quotas and an unchecked fallback, while the offline evaluator modeled shared directed-edge occupancy. Its earlier 1,000-request experiment assigned 444 commuters and showed admitted-only modeled dose **+0.1211%** and time **+0.1463%** relative to its comparator. v2t preserved both historical versions and introduced a corrected serving allocator with route-plus-edge quotas, atomic displacement and UNASSIGNED results. Twenty focused tests passed; a 36-cell central-Bengaluru benchmark found zero saved-output capacity violations but only 5.405% maximum edge utilization. The corrected and original serving paths matched on all 1,008 scenario requests, with negligible dose/time differences. Neither real-world exposure reduction nor universal preference stability follows. [EVIDENCE: `final_blr_results/final_routing_closure/original_gale_shapley_audit/PREVIOUS_BENCHMARK_RECONCILIATION.md`; `final_blr_results/final_routing_closure/v2t/ROUTING_FINAL_VERDICT.md` | snapshot `1c46a4b`]\n',
      '## Evidence hierarchy and numerical comparison\n',
      '| Result | Population / protocol | Finding | Permitted interpretation |\n|---|---|---|---|',
      '| Original paper MAE 53.14 / 75.35 / 62.51 µg/m³ and PVR 1.404% | Original manuscript claimed, PDF unavailable | Historically reported by author; source table unavailable | Do not reuse as corrected accuracy |',
      '| v2j/v2l directional versus λ=0 | 14,583 matched station pairs/horizon, five seeds | ΔMAE h=3 −0.130, h=6 −0.410, h=12 −0.262, h=24 +0.145 µg/m³ | Exploratory horizon-dependent association; no physical specificity |',
      '| W6 spatial holdout | Eleven scored stations | ST-PIGNN 22.314, ridge 20.624 µg/m³ MAE | No demonstrated station-transfer superiority |',
      '| v2r compact decoder | Eleven sites, 14,583 common test pairs | Decoder 27.360, forecast-IDW 20.154, mean 20.634 µg/m³ MAE | Negative spatial-decoder result |',
      '| v2r road expansion | Three h=6 times × 154,902 road nodes | 464,706 finite estimates | Computational demonstration; no road accuracy |',
      '| v2t serving allocation | 1,008 scenario requests, four fields | 0 violations, all assigned, max edge utilization 5.405% | Software feasibility in an unstressed assumed-quota scenario |\n',
      '## Mathematical and engineering boundaries\n',
      'The directional penalty may be written schematically as a masked geometric weighted squared hinge, \(L_{dir}=\sum M_{ij,t}g_{ij}[\max(0,\hat y_{j,t}-\hat y_{i,t})]^2/(\sum M_{ij,t}+\epsilon)\). Its sign and normalization are code-specific. It does not measure net air-mass flux. A dimensioned finite-volume balance requires \(V\Delta C/\Delta t+\sum_f F_f=V(S-R)\) with atmospheric cells, boundary fluxes and sources, none of which were validated for historical ST-PIGNN. For modeled routing dose, \(D_e=C_e R L_e/v\) gives µg when concentration, ventilation, distance and speed have compatible units. It is an estimate conditional on an unvalidated concentration field and assumed breathing rate. Exact versioned equations are in the [equation register](appendices/COMPLETE_EQUATION_REGISTER.md).\n',
      '## Chapter map\n']
    for code,title,paths in VOLUMES:
      master += [f'### {int(code[:2])}. {title}\n',
                 f'{FRAMES[code[:2]]}\n',
                 f'Full treatment: [Volume {int(code[:2])}](volumes/VOLUME_{code}.md), with {len(paths)} complete source exhibits.\n']
    master += ['## Final scientific position\n',
      'The strongest defensible result is a reproducible, protocol-labeled station forecasting and engineering record with honest controls and negative findings. A better test MAE at selected horizons does not prove physical transport. A map covering every road node does not establish roadside concentration accuracy. A capacity-feasible algorithm does not establish actual commuter exposure reduction or stable matching under overlapping route bundles. A numerical conservation diagnostic does not retroactively change old model weights. RGDR is an unvalidated hypothesis stopped by sparse optimization exposure. The unresolved scientific work is independent spatial sensing and prospective replication under a frozen protocol.\n',
      'For exact machine-readable values, use the [results register](appendices/COMPLETE_RESULTS_REGISTER.md), [copied source tables](tables/TABLE_SOURCE_MAP.csv), [claim matrix](appendices/COMPLETE_CLAIM_EVIDENCE_MATRIX.md), [failure log](appendices/COMPLETE_FAILURE_AND_CORRECTION_LOG.md), and [verification report](reproducibility/MONOGRAPH_VERIFICATION_REPORT.md). Original PDF/review absence, missing checkpoints and backup status are listed in the [unresolved issues](appendices/COMPLETE_UNRESOLVED_ISSUES.md).\n']
    (BASE/'ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH.md').write_text('\n'.join(master))
    (BASE/'EXECUTIVE_RESEARCH_HISTORY.md').write_text('# Executive research history\n\n'+'\n\n'.join([f'## {int(code[:2])}. {title}\n\n{FRAMES[code[:2]]}' for code,title,_ in VOLUMES])+'\n')
    (BASE/'README.md').write_text('# ST-PIGNN complete research monograph\n\nStart with [the master document](ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH.md), then [the contents](TABLE_OF_CONTENTS.md). The 16 volumes contain editorial analysis plus full traceable research exhibits. The 15 appendices and copied CSV tables preserve machine evidence. The original rejected PDF and six full reviews are absent; volume 1/2 are source-limited and clearly marked. No experiment is run by these documentation builders. Use `python build_monograph.py`, `python build_appendices.py`, and `python verify_monograph.py` from this directory after ensuring the source repository is present. Markdown is authoritative.\n')
    progress=['# Monograph progress and source limits\n',
      'Status vocabulary: NOT STARTED, IN PROGRESS, SOURCE VERIFIED, WRITTEN, CROSS-CHECKED, COMPLETE, BLOCKED BY MISSING SOURCE. An exhibit being embedded means its bytes were read; it does not establish that the underlying experiment is independently reproducible.\n',
      '| Unit | Status | Source state |\n|---|---|---|']
    for code,title,paths in VOLUMES:
      status='BLOCKED BY MISSING SOURCE' if code[:2] in {'01','02'} else 'WRITTEN'
      reason='Original submitted PDF and six full reviews missing; recoverable implementation and issue-level evidence included.' if code[:2] in {'01','02'} else f'{len(paths)} complete local reports embedded; final consistency audit pending.'
      progress.append(f'| Volume {int(code[:2])}: {title} | {status} | {reason} |')
    progress += ['\nAppendices are generated from saved registries and copied tables. No chapter is marked COMPLETE before source, numerical and link verification. Next: inspect generated appendices, run independent checks, document discrepancies, archive and publish.\n']
    (BASE/'MONOGRAPH_PROGRESS.md').write_text('\n'.join(progress))
    print(json.dumps({'volumes': len(VOLUMES), 'unique_embedded_sources':len(coverage),
                      'volume_words':sum(len((BASE/'volumes'/f'VOLUME_{c}.md').read_text().split()) for c,_,_ in VOLUMES)},indent=2))

if __name__ == '__main__':
    main()
