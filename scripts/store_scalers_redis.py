import json
from redis import Redis
from pathlib import Path

p = Path('data/processed/per_zone_scalers.json')
if not p.exists():
    raise SystemExit('per_zone_scalers.json not found')

with open(p) as fh:
    data = json.load(fh)

r = Redis.from_url('redis://localhost:6379', decode_responses=True)
for zid, v in data.items():
    key = f'scaler:{zid}'
    a = float(v.get('a', 1.0))
    b = float(v.get('b', 0.0))
    n = int(v.get('n', 0))
    r.hset(key, mapping={'a': a, 'b': b, 'version': 'auto_fit', 'min_samples': n})
    print('wrote', key, '->', a, b, 'n=', n)
print('done')
