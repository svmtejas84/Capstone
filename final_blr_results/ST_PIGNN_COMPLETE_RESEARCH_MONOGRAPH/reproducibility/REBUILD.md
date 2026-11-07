# Monograph regeneration

Run from the Capstone repository root, with the frozen Bengaluru reports present:

1. `python final_blr_results/ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH/build_monograph.py`
2. `python final_blr_results/ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH/build_appendices.py`
3. `python final_blr_results/ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH/verify_monograph.py`
4. `python final_blr_results/ST_PIGNN_COMPLETE_RESEARCH_MONOGRAPH/package_monograph.py`

These commands read reports, tables, figures, the original production notebook and Git history. They do not train a model, run the historical notebook, change prior experiments or generate new scientific results. The generated reports intentionally use repository snapshot `1c46a4b605f2d8e8ba25a407ace756e675a8aa15` as the frozen source baseline. After a source transfer or later correction, create a new documented edition rather than silently changing that snapshot. The archive omits raw datasets and model checkpoints; original inputs and checkpoint gaps remain recorded in the source reports. The original submitted PDF and six complete reviews are still required to resolve Volumes 1–2. A PDF edition was not generated because `pandoc` is unavailable; the Markdown edition is authoritative.
