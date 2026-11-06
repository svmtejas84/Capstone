from pathlib import Path
import hashlib,csv,sys
root=Path('final_blr_results/ieee_paper_evidence'); bad=[]; n=0
with (root/'reproducibility/CHECKSUMS.csv').open(newline='') as f:
 for r in csv.DictReader(f):
  p=root/r['relative_path']; n+=1
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256'] or p.stat().st_size!=int(r['bytes']):bad.append(r['relative_path'])
print(f'verified {n-len(bad)}/{n} package files')
if bad: print('mismatches:',', '.join(bad));sys.exit(1)
