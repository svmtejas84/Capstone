"""Resume W6 folds and mark the supervised run complete only after summary."""
from scripts.evaluate_loso_v2j import main
from src.stpignn.paths import REPO_ROOT

if __name__ == "__main__":
    main()
    (REPO_ROOT / "results/codex_log/runs/loso_v2j/COMPLETE").write_text("LOSO complete\n")
