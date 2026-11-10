from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from src.stpignn.data_v2 import build
OUT=ROOT/'final_blr_results/ieee_publication_assets_v2v'
data,_=build(ROOT/'configs/data_v2.yaml',weather_half_hour_rule=True,weather_cutoff_safe=False)
rows=[]
for split,tm in data.split_masks.items():
 raw=data.raw_values[tm]
 for j in range(raw.shape[-1]):
  name=data.feature_registry[j]['name']
  if name=='pm25_lagged':
   # The value channel was already causally imputed in raw_values; retain observed-mask missingness separately.
   observed=data.observed_mask[tm]
   frac=float((~observed).mean())
   n=int((~observed).sum())
   note='Raw PM2.5 target availability; input value has train-fitted causal imputation and a separate lag_is_imputed channel'
  else:
   frac=float((~np.isfinite(raw[:,:,j])).mean()); n=int((~np.isfinite(raw[:,:,j])).sum())
   note='Raw feature missing before _causal_fill; fitted fill uses train median and bounded forward fill'
  rows.append({'split':split,'feature':name,'unit':data.feature_registry[j]['units'],'missing_count':n,
               'total_station_hours':int(raw.shape[0]*raw.shape[1]),'missing_fraction':frac,'handling':note})
pd.DataFrame(rows).to_csv(OUT/'source_data/DATA_per_feature_missingness.csv',index=False)
print('saved',len(rows),'split-feature rows')
