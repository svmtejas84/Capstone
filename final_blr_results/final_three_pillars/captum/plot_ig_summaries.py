"""Create publication-readable, descriptive IG summaries by version."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
for sub, title in [(ROOT, "v2c corrected ST-PIGNN, h=1"),
                   (ROOT / "v2r_heldout_h6", "v2r corrected ST-PIGNN, h=6 outer LOSO")]:
    frame = pd.read_csv(sub / "feature_summary.csv")
    name = next((c for c in frame if c.lower() in ("feature", "feature_name")), None)
    score = next((c for c in frame if "mean_abs" in c.lower() or "absolute" in c.lower()), None)
    if name is None or score is None:
        raise ValueError(f"Expected named feature and mean absolute attribution columns: {frame.columns.tolist()}")
    frame = frame.sort_values(score).tail(12)
    fig, ax = plt.subplots(figsize=(8.2, 5.4), constrained_layout=True)
    ax.barh(frame[name].astype(str), frame[score], color="#356b8c")
    ax.set_xlabel("Mean absolute attribution (µg/m³ output scale; baseline-relative)")
    ax.set_ylabel("Input feature")
    ax.set_title(title + " — selected examples; not causal importance")
    fig.text(.01, .005, "Source: versioned Captum IG rows; fixed selected examples. Model protocols differ; do not compare panel magnitudes across versions.", fontsize=8)
    fig.savefig(sub / "figures" / "ig_feature_summary.png", dpi=220)
    fig.savefig(sub / "figures" / "ig_feature_summary.pdf")
    plt.close(fig)
