import pandas as pd
from pathlib import Path

sources = {
	'weather': 'data/raw/weather',
	'airquality': 'data/raw/airquality',
	'stations': 'data/raw/stations',
}

for source, folder in sources.items():
	print(f'\n── {source.upper()} ──')
	for f in sorted(Path(folder).glob('*.parquet')):
		try:
			df = pd.read_parquet(f)
			total = df.size
			missing = df.isnull().sum().sum()
			pct = (missing / total) * 100 if total > 0 else 0
			print(f' {f.name}: {len(df):>10,} rows | {missing:>8,} missing | {pct:.1f}%')
		except Exception as e:
			print(f' {f.name}: ERROR — {e}')