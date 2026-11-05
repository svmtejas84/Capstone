"""Plot the saved-prediction MAE table; no training."""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

base=Path(__file__).resolve().parents[1]
data=pd.read_csv(base/"comparisons/ensemble_metrics.csv")
fig,ax=plt.subplots(figsize=(7,4))
for model,label in (("mlp","MLP (cutoff-safe)"),("tcn","TCN (cutoff-safe)"),
                    ("stpignn_original","ST-PIGNN (historical centered)"),
                    ("persistence","Persistence"),("same_hour_yesterday","Same hour yesterday")):
    z=data[data.model==model].sort_values("horizon_hours")
    ax.plot(z.horizon_hours,z.mae,marker="o",label=label)
ax.set(xlabel="Forecast horizon (hours)",ylabel="Test MAE (µg/m³)",xticks=[1,3,6,12,24])
ax.grid(alpha=.2)
ax.legend(fontsize=8)
fig.tight_layout()
out=base/"figures/mae_by_horizon_v2m.png"
out.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(out,dpi=180)
print(out)
