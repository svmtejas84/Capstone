
import json
from pathlib import Path
import nbformat

def extract_target_scale(notebook_path: Path) -> float | None:
    """Extracts the TARGET_SCALE value from a Jupyter notebook."""
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)
    
    for cell in nb.cells:
        if cell.cell_type == "code":
            # More robustly find the TARGET_SCALE line
            source_lines = cell.source.splitlines()
            for line in source_lines:
                if "TARGET_SCALE" in line and "=" in line:
                    try:
                        # Extract the float value
                        scale_value = float(line.split("=")[1].strip())
                        return scale_value
                    except (ValueError, IndexError):
                        continue
    return None

def main():
    """
    Extracts the target scale from the training notebook and saves it to a
    JSON file.
    """
    notebook_path = Path("notebooks/cluster_working.ipynb")
    scale = extract_target_scale(notebook_path)

    if scale is None:
        print("TARGET_SCALE not found in the notebook.")
        return

    scaler_path = Path("gnn/model_weights/target_scaler.json")
    scaler_path.parent.mkdir(parents=True, exist_ok=True)
    with open(scaler_path, "w") as f:
        json.dump({"type": "max_abs", "value": scale}, f, indent=2)
    
    print(f"Scaler saved to {scaler_path}")

if __name__ == "__main__":
    main()
