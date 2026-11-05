"""Resume fixed h=1/24 lambda cells and mark supervised completion."""
from scripts.lambda_check_v2j import main
from src.stpignn.paths import REPO_ROOT

if __name__ == "__main__":
    main()
    (REPO_ROOT / "results/codex_log/runs/lambda_v2j/COMPLETE").write_text("lambda check complete\n")
