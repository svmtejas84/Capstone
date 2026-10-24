"""Move the notebook's Captum adapter to src and correct its channel labels."""
import ast
import json

from src.stpignn.paths import asset


def main():
    path = asset("notebooks/production/evaluated_wind_advection.ipynb")
    notebook = json.loads(path.read_text())
    cell = notebook["cells"][14]
    source = "".join(cell["source"])
    lines = source.splitlines(keepends=True)
    klass = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef) and node.name == "CaptumGNNWrapper")
    source = "".join(lines[:klass.lineno - 1]) + "from src.stpignn.explain import CaptumGNNWrapper\n" + "".join(lines[klass.end_lineno:])
    begin = source.index("feature_names = [")
    end = source.index("\n\nabs_attributions", begin)
    source = source[:begin] + "feature_names = FEATURE_COLS_16" + source[end:]
    cell["source"] = source.splitlines(keepends=True)
    cell["outputs"] = []
    cell["execution_count"] = None
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
