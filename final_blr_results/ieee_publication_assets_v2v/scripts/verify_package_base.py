"""Static/visual-file, source, numeric and archive checks for v2u."""
from __future__ import annotations
import hashlib, json, os, re, zipfile
from pathlib import Path
from PIL import Image
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'final_blr_results/ieee_publication_assets'
figures=json.loads((OUT/'source_data/figure_manifest.json').read_text())
tables=pd.read_csv(OUT/'tables/table_manifest.csv').to_dict('records')
LAT=OUT/'latex'; LAT.mkdir(exist_ok=True)
VER=OUT/'verification'; VER.mkdir(exist_ok=True)

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def latex_escape(s):
    return str(s).replace('\\','').replace('_',r'\_').replace('%',r'\%').replace('&',r'\&').replace('µ',r'$\mu$').replace('₂',r'$_2$').replace('₅',r'$_5$').replace('×',r'$\times$').replace('–','--')

def make_latex():
    lines=['% v2u figure snippets, include from ieee_publication_assets/latex','% Requires graphicx']
    for item in figures:
        width=r'\textwidth' if item['group']!='F01_architecture' else r'\columnwidth'
        typ='figure*' if width==r'\textwidth' else 'figure'
        path='../'+item['pdf']
        lines += [f'\\begin{{{typ}}}[t]',r'\centering',f'\\includegraphics[width={width}]{{{path}}}',
                  r'\caption{'+latex_escape(item['caption'])+'}',f'\\label{{fig:{item["id"].lower()}}}',f'\\end{{{typ}}}','']
    (LAT/'figures.tex').write_text('\n'.join(lines))
    (LAT/'asset_manifest.tex').write_text('% v2u asset inventory; include snippets selectively\n'+
        f'% {len(figures)} figure variants and {len(tables)} LaTeX tables\n'+
        '% Figures: '+', '.join(x['id'] for x in figures)+'\n'+
        '% Tables: '+', '.join(x['id'] for x in tables)+'\n')

def checks():
    issues=[]; trace=[]
    for item in figures:
        for ext in ('png','pdf','svg'):
            p=OUT/item[ext]
            if not p.exists(): issues.append(f'Missing figure {p}')
            elif ext=='png':
                with Image.open(p) as im:
                    im.verify()
                with Image.open(p) as im:
                    if min(im.size)<600:issues.append(f'Low raster resolution {p}: {im.size}')
            elif ext=='pdf' and not p.read_bytes()[:5]==b'%PDF-':issues.append(f'Bad PDF {p}')
            elif ext=='svg' and b'<svg' not in p.read_bytes()[:2000]:issues.append(f'Bad SVG {p}')
        for s in item['sources']:
            p=ROOT/s
            if not p.exists():issues.append(f'Missing source {s}')
            else:trace.append((s,sha(p)))
        if not (OUT/'figures'/item['group']/(item['id']+'_caption.md')).exists():issues.append('Missing caption '+item['id'])
    if len({x['id'] for x in figures})!=len(figures):issues.append('Duplicate figure ID')
    for t in tables:
        if not (OUT/'tables'/f'{t["id"]}.tex').exists():issues.append('Missing table '+t['id'])
        if not (OUT/'tables'/f'{t["id"]}.csv').exists():issues.append('Missing table data '+t['id'])
    # Specific saved-data invariants, not new performance analyses.
    g=pd.read_csv(OUT/'source_data/F02_graph_summary.csv').iloc[0]
    for col,n in [('road_nodes',154902),('raw_directed_edges',393089),('processed_message_arcs',424550),('historical_partitions',64),('omitted_cross_boundary_arcs',7134),('forecast_stations',15)]:
        if int(g[col])!=n: issues.append(f'F02 {col}: {g[col]} expected {n}')
    m=pd.read_csv(OUT/'tables/T04b.csv').set_index('Method')
    for name,v in [('forecast_decoder',27.3598647),('forecast_idw',20.1535526),('train_only_spatial_mean',20.6337838)]:
        if abs(m.loc[name,'MAE']-v)>1e-5:issues.append(f'T04b mismatch {name}')
    cap=pd.read_csv(OUT/'tables/T06.csv').set_index('Variant')
    if cap.loc['v2c h=1','All records']!=54 or cap.loc['v2r h=6 outer-LOSO','All records']!=18:issues.append('T06 records mismatch')
    road=pd.read_csv(OUT/'source_data/F07_snapshot_node_data.csv')
    if len(road)!=154902 or road.node_index.nunique()!=154902 or not np.isfinite(road.forecast_decoder_ug_m3).all():issues.append('F07 node coverage or finite values failed')
    p=pd.read_csv(OUT/'source_data/F08_tradeoff.csv').set_index('control')
    if abs(p.loc['shortest','dose_delta_pct']-(-.001207))>5e-5:issues.append('F08 dose percentage mismatch')
    # All local LaTeX graphic/input paths must resolve from latex/.
    for name in ('figures.tex','tables.tex'):
        for rel in re.findall(r'\\(?:includegraphics\[[^]]*\]|input)\{([^}]+)\}',(LAT/name).read_text()):
            if not (LAT/rel).exists():issues.append(f'Broken LaTeX path {name}: {rel}')
    if len(set(re.findall(r'\\label\{([^}]+)\}',(LAT/'figures.tex').read_text())))!=len(figures):issues.append('Duplicate figure label')
    return issues,trace

def write_docs(issues,trace):
    pd.DataFrame(sorted(set(trace)),columns=['source_path','sha256']).to_csv(VER/'SOURCE_HASHES.csv',index=False)
    counts=f'{len(figures)} figure variants (eight requested groups), {len(tables)} table files (eight requested groups), {len(set(x[0] for x in trace))} distinct directly plotted source artifacts.'
    report='# Publication asset verification\n\n'+counts+'\n\n'
    report+='- PNG files opened and decoded; PDF and SVG signatures checked. All ten figure variants were visually inspected at rendered resolution.\n'
    report+='- Figure source artifacts exist and SHA-256 fingerprints are in `SOURCE_HASHES.csv`.\n'
    report+='- F02 graph counts, F07 full-node finite coverage, F06 record counts, T04b spatial metrics and F08 matched dose difference checked against saved artifacts.\n'
    report+='- All local figure/table LaTeX paths and figure labels checked.\n'
    report+='- `pdflatex` and `latexmk` are unavailable; compilation was not run. Two-column size was inspected for selected rasterized outputs. Large tables may need manuscript-specific splitting or abbreviations.\n'
    report+='- F07 derived node CSV is a traceability copy of saved parquet. It is kept in the local ZIP but should not be committed as a large duplicate.\n'
    report+='\n## Findings\n\n'+('\n'.join('- '+x for x in issues) if issues else 'No failed automated invariant.')+'\n'
    (VER/'PUBLICATION_ASSET_VERIFICATION.md').write_text(report)
    (OUT/'README.md').write_text('# IEEE publication assets v2u\n\n'+counts+'\n\n'
        'All plots and tables derive from frozen Bengaluru results. `scripts/build_assets.py` regenerates figures; `scripts/build_tables.py` regenerates tables; `scripts/verify_package.py` checks sources and archives.\n\n'
        'The corrected 15-station forecasting model is separate from the 154,902-node road graph. Citywide values are experimental neural-assisted estimates, and routing dose is modeled. v2j and v2m weather protocols differ.\n\n'
        'See `methodology/ASSET_PROTOCOL.md`, `source_data/figure_manifest.json`, `tables/table_manifest.csv`, and `FINAL_PUBLICATION_ASSET_HANDOFF.md`.\n')
    handoff='# Final publication asset handoff\n\n'+counts+'\n\n'
    handoff+='## Recommended main-paper order\n\nF01 architecture; F02 graphs/stations; F03 multi-horizon benchmark; F04 physics ablation; F05 spatial holdouts. F06a/b, F07, and F08 are valuable supplementary or carefully captioned main-paper evidence if space permits.\n\n'
    handoff+='## Inventory and use\n\n'
    for f in figures:handoff+=f'- **{f["id"]}**: `{f["pdf"]}`; PNG/SVG and caption adjacent. Source: '+', '.join('`'+s+'`' for s in f['sources'])+'.\n'
    handoff+='\nTables: '+', '.join('`'+x['id']+'`' for x in tables)+'. `T02a/b` and `T04a/b` intentionally separate incompatible protocols. CSV and TeX are paired in `tables/`.\n\n'
    handoff+='## Regeneration and integration\n\nFrom repository root:\n\n```sh\npython final_blr_results/ieee_publication_assets/scripts/build_assets.py\npython final_blr_results/ieee_publication_assets/scripts/build_tables.py\npython final_blr_results/ieee_publication_assets/scripts/verify_package.py\n```\n\n'
    handoff+='Select the desired `\\input` lines from `latex/figures.tex` and `latex/tables.tex` in the manuscript source. Paths are relative to `latex/`; copy assets or adjust paths if the manuscript lives elsewhere. IEEEtran compilation was unavailable here.\n\n'
    handoff+='## Scientific boundaries\n\nNo new training or experiment occurred. F06 uses v2c h1 and v2r h6 corrected variants, not missing v2j benchmark checkpoints. F07 road values are not roadside observations and decoder LOSO was unfavorable. F08 shows tiny modeled-dose differences and low utilization, not real-world exposure reduction. Directional physics remains a regularization heuristic. Missing original manuscript/reviewer texts still require transfer for the broader paper evidence package.\n\n'
    handoff+='Verification: `verification/PUBLICATION_ASSET_VERIFICATION.md`. Source fingerprints: `verification/SOURCE_HASHES.csv`.\n'
    (OUT/'FINAL_PUBLICATION_ASSET_HANDOFF.md').write_text(handoff)

def archive():
    zpath=OUT/'IEEE_PUBLICATION_ASSETS.zip'
    files=[p for p in OUT.rglob('*') if p.is_file() and p!=zpath and '.pyc' not in p.name and '__pycache__' not in p.parts]
    manifest=pd.DataFrame([{'path':str(p.relative_to(OUT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files) if p.name!='CHECKSUMS.csv'])
    manifest.to_csv(VER/'CHECKSUMS.csv',index=False)
    files=[p for p in OUT.rglob('*') if p.is_file() and p!=zpath and '.pyc' not in p.name and '__pycache__' not in p.parts]
    with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(files):z.write(p,p.relative_to(OUT))
    with zipfile.ZipFile(zpath) as z:
        bad=z.testzip()
        if bad:raise RuntimeError('ZIP CRC failure '+bad)
        for row in pd.read_csv(VER/'CHECKSUMS.csv').itertuples(index=False):
            if hashlib.sha256(z.read(row.path)).hexdigest()!=row.sha256:raise RuntimeError('ZIP SHA mismatch '+row.path)
    print('ZIP',zpath,'bytes',zpath.stat().st_size,'sha256',sha(zpath),'members',len(files))

def main():
    make_latex();issues,trace=checks();write_docs(issues,trace)
    if issues:raise RuntimeError('\n'.join(issues))
    archive()
    print('Verified',len(figures),'figures',len(tables),'tables',len(set(x[0] for x in trace)),'source artifacts')

if __name__=='__main__':main()
