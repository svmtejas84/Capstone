"""Plot v2o estimates with poor-support road nodes explicitly masked gray."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

OUT=Path(__file__).resolve().parent
indices=json.loads((OUT/"selected_snapshots.json").read_text())["indices"]
df=pd.read_parquet(OUT/"road_node_estimates.parquet")
for index,(_,part) in zip(indices,df.groupby("target_time_utc",sort=True)):
    fig,ax=plt.subplots(figsize=(9,8),constrained_layout=True)
    poor=part[part.poor_support]
    good=part[~part.poor_support]
    ax.scatter(poor.utm_x_m,poor.utm_y_m,c="lightgray",s=0.15,rasterized=True,label="poor support: outside hull or >5 km")
    s=ax.scatter(good.utm_x_m,good.utm_y_m,c=good.estimate_ug_m3,s=0.3,cmap="viridis",rasterized=True)
    fig.colorbar(s,ax=ax,label="retrospective IDW estimate (µg/m³), supported subset")
    ax.set_title(f"{part.target_time_utc.iloc[0]} — IDW estimate; gray nodes poorly supported")
    ax.set_xlabel("UTM east (m)");ax.set_ylabel("UTM north (m)")
    ax.legend(markerscale=30,loc="lower left")
    fig.savefig(OUT/f"citywide_idw_{index}.png",dpi=150)
    plt.close(fig)
