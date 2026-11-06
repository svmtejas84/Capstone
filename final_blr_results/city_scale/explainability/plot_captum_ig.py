"""Regenerate descriptive v2n IG figures from frozen saved tensors and metadata."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
d = pd.read_csv(OUT / "convergence_diagnostics.csv")
z = np.load(OUT / "attribution_tensors.npz")
a = z["attributions"]
names = list(z["feature_names"])
assert len(d) == len(a) == 228

for model in ("mlp", "tcn"):
    mask = (d.model == model) & (d.seed == 11) & (d.baseline == "training_mean")
    signed = a[mask.to_numpy()].mean(axis=0)
    absolute = np.abs(a[mask.to_numpy()]).mean(axis=0)
    fig, ax = plt.subplots(1, 2, figsize=(17, 6), constrained_layout=True)
    scale = max(abs(signed.min()), abs(signed.max()))
    x = ax[0].imshow(signed, aspect="auto", cmap="coolwarm", vmin=-scale, vmax=scale)
    fig.colorbar(x, ax=ax[0], label="mean signed IG (µg/m³)")
    y = ax[1].imshow(absolute, aspect="auto", cmap="viridis")
    fig.colorbar(y, ax=ax[1], label="mean absolute IG (µg/m³)")
    for axis, title in zip(ax, ("signed", "absolute")):
        axis.set_title(f"{model.upper()} {title}, seed 11, training mean baseline")
        axis.set_xticks(range(18), names, rotation=75, ha="right")
        axis.set_yticks(range(12), [str(11-k) for k in range(12)])
        axis.set_ylabel("hours before cutoff")
    fig.savefig(OUT / f"ig_feature_temporal_{model}.png", dpi=150)
    plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 4), constrained_layout=True)
for model in ("mlp", "tcn"):
    mask = (d.model == model) & (d.seed == 11) & (d.baseline == "training_mean")
    v = np.abs(a[mask.to_numpy()]).sum(axis=2).mean(axis=0)
    ax.plot(range(11, -1, -1), v, marker="o", label=model.upper())
ax.set_xlabel("hours before cutoff")
ax.set_ylabel("mean absolute IG summed over features (µg/m³)")
ax.legend()
fig.savefig(OUT / "ig_temporal_summary.png", dpi=150)
plt.close(fig)
