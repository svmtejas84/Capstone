from pathlib import Path
import csv,json,hashlib,sys,re
from PIL import Image
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
errors=[]
fm=json.loads((P/'source_data/figure_manifest.json').read_text())
for x in fm:
 for key in ('png','pdf','svg'):
  q=P/x[key]
  if not q.exists() or q.stat().st_size==0: errors.append(f'missing/empty {q}')
 if (P/x['png']).exists():
  try:
   im=Image.open(P/x['png']); im.verify()
  except Exception as e: errors.append(f'bad PNG {x["png"]}: {e}')
 for src in x.get('sources',[]):
  if not (ROOT/src).is_file(): errors.append(f'missing source artifact {src}')
for q in sorted((P/'tables').glob('T*.csv')):
 with q.open(newline='') as f:
  rows=list(csv.reader(f))
  if len(rows)<2: errors.append(f'empty table {q}')
for q in [P/'latex/figures.tex',P/'latex/tables.tex']:
 if not q.exists(): errors.append(f'missing {q}')
 if q.exists():
  for ref in re.findall(r'\\(?:includegraphics\[[^]]*\]|input)\{([^}]+)\}',q.read_text()):
   if not (ROOT/ref).exists(): errors.append(f'unresolved TeX asset {ref}')
# Provenance files must be present; source existence recorded separately for external/local large inputs.
for rel in ['captions/PUBLICATION_FIGURE_CAPTIONS.md','analyses/DATA_PROVENANCE_AND_MISSINGNESS_AUDIT.md','analyses/METHOD_IMPLEMENTATION_FACTS.md','analyses/MODEL_VARIANT_AND_SELECTION_AUDIT.md','analyses/OPTIONAL_EXPERIMENTS_VERDICT.md']:
 if not (P/rel).exists(): errors.append(f'missing evidence document {rel}')
if errors:
 print('FAIL'); print('\n'.join(errors)); sys.exit(1)
print(f'PASS: {len(fm)} figure records, {sum(1 for _ in (P/"tables").glob("T*.csv"))} CSV tables; all PNGs decode; PDF/SVG files nonempty; source artifacts and LaTeX paths resolve')
