# Publication asset verification

10 figure variants (eight requested groups), 10 table files (eight requested groups), 17 distinct directly plotted source artifacts.

- PNG files opened and decoded; PDF and SVG signatures checked. All ten figure variants were visually inspected at rendered resolution.
- Figure source artifacts exist and SHA-256 fingerprints are in `SOURCE_HASHES.csv`.
- F02 graph counts, F07 full-node finite coverage, F06 record counts, T04b spatial metrics and F08 matched dose difference checked against saved artifacts.
- All local figure/table LaTeX paths and figure labels checked.
- `pdflatex` and `latexmk` are unavailable; compilation was not run. Two-column size was inspected for selected rasterized outputs. Large tables may need manuscript-specific splitting or abbreviations.
- F07 derived node CSV is a traceability copy of saved parquet. It is kept in the local ZIP but should not be committed as a large duplicate.

## Findings

No failed automated invariant.
