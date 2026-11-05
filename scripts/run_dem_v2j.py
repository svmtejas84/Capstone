"""Resume the fixed W3 DEM cells and mark supervised completion."""
from scripts.dem_study_v2j import main
from src.stpignn.paths import REPO_ROOT

if __name__ == "__main__":
    main()
    (REPO_ROOT / "results/codex_log/runs/dem_v2j/COMPLETE").write_text("DEM study complete\n")
