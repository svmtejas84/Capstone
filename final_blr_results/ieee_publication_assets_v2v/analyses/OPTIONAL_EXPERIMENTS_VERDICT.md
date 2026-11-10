# Optional experiment suggestions — not executed

No new model training or test-selected experiments were performed in this asset-correction round.

| Suggested analysis | Scientific question | Existing evidence sufficient? | Status |
|---|---|---|---|
| Shuffled-wind control | Does the directional model's benefit require the observed wind-to-edge alignment rather than generic edge conditioning? | No. Saved predictions contain no matched shuffled-wind fit. | NOT RUN; would require new training and a frozen validation/test protocol. |
| Rotated-wind control | Does rotating directions disrupt the learned/regularized signal under matched geometry? | No. Requires new fits; cannot be reconstructed from ordinary predictions. | NOT RUN. |
| Lambda sensitivity | How do multiple fixed λ values affect accuracy and diagnostics under matched training? | Existing historical sweeps are not a clean, prospective sensitivity family for the corrected v2j protocol. | NOT RUN in v2v; preserve prior sweep evidence with its own protocol labels. |
| Directional-cone-width sensitivity | Are findings robust to cone angle? | The corrected model uses 37.5°; no matched trained cone-width series is available. | NOT RUN. |
| Cutoff-safe ST-PIGNN retraining | Would a corrected ST-PIGNN under forecast-origin-safe meteorology retain prior results? | No. MLP/TCN cutoff-safe results cannot substitute for ST-PIGNN retraining. | NOT RUN; would require separate supervisor authorization and a new frozen evaluation. |

The present package only corrects saved evidence. It does not infer outcomes for any unrun control.
