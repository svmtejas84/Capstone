# Original production notebook cell map

Source `notebooks/production/evaluated_wind_advection.ipynb`; SHA-256 `242d0cf3d2f95c78a011841ed2aec2e100cc8c326e6211c918a8bd70504b8161`. Static inspection only; no cell executed. Twenty-six code cells, no saved outputs or markdown cells.

| Cell | Lines | Definitions/imports (first occurrences) |
|---:|---:|---|
| 0 | 94 | import os; import sys; import gc; import time; import random; from pathlib import Path |
| 1 | 29 | No top-level definition/import in first static scan |
| 2 | 87 | import numpy as np; import pandas as pd; import torch; from sklearn.cluster import KMeans; from src.stpignn.legacy_canonical import SpatialPartition |
| 3 | 35 | No top-level definition/import in first static scan |
| 4 | 91 | import gc; import numpy as np; import pandas as pd; import torch; from tqdm.auto import tqdm; FEATURE_COLS_16 = [ |
| 5 | 93 | import gc; import numpy as np; import pandas as pd; import torch; from scipy.spatial import KDTree; from tqdm.auto import tqdm |
| 6 | 36 | No top-level definition/import in first static scan |
| 7 | 38 | import numpy as np; import torch; from src.stpignn.legacy_canonical import compute_dynamic_upwind_mask_vectorized as _legacy_mask; def compute_dynamic_upwind_mask_vectorized(cluster_obj, current_wind_dir_deg, cone_angle_deg=75.0): |
| 8 | 25 | import time |
| 9 | 77 | import numpy as np; import pandas as pd; import torch; import gc; from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler; from src.stpignn.legacy_canonical import TierAwareClusterDatasetV3 |
| 10 | 23 | No top-level definition/import in first static scan |
| 11 | 43 | import torch; import torch.amp |
| 12 | 28 | No top-level definition/import in first static scan |
| 13 | 239 | import os; import time; import gc; import numpy as np; import torch; import torch.nn.functional as F |
| 14 | 96 | import os; import torch; import numpy as np; import pandas as pd; from captum.attr import IntegratedGradients; from src.stpignn.explain import CaptumGNNWrapper |
| 15 | 138 | import os; import numpy as np; import pandas as pd; import torch; from sklearn.metrics import r2_score; from tqdm.auto import tqdm |
| 16 | 143 | import os; import numpy as np; import pandas as pd; import torch; from sklearn.metrics import r2_score; from tqdm.auto import tqdm |
| 17 | 139 | import os; import numpy as np; import pandas as pd; import torch; from sklearn.metrics import r2_score; from tqdm.auto import tqdm |
| 18 | 80 | import numpy as np; import pandas as pd; import torch; import matplotlib.pyplot as plt; from scipy.interpolate import griddata |
| 19 | 124 | import os; import gc; import numpy as np; import pandas as pd; import torch; import matplotlib.pyplot as plt |
| 20 | 94 | import os; import numpy as np; import pandas as pd; import torch; from tqdm.auto import tqdm; from src.stpignn.legacy_canonical import compute_dynamic_upwind_mask_vectorized as _legacy_mask |
| 21 | 88 | import numpy as np; import torch; import matplotlib.pyplot as plt |
| 22 | 17 | import torch; import torch.nn as nn; from torch_geometric.nn import GCNConv; from src.stpignn.legacy_canonical import VanillaGCN; from src.stpignn.legacy_canonical import ST_GRUGCN |
| 23 | 98 | import time; import numpy as np; import torch; from tqdm.auto import tqdm |
| 24 | 51 | import numpy as np; import torch; from src.stpignn.legacy_canonical import legacy_global_metrics |
| 25 | 0 | No top-level definition/import in first static scan |
