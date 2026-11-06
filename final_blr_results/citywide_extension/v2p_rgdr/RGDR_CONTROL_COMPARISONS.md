# RGDR matched controls: implementation versus outcome

| Control | Formula available now | Trained matched checkpoint | Validation prediction comparison |
|---|---|---|---|
| λ=0 | existing corrected ST-PIGNN loss with no physics term | No new v2p checkpoint | NOT RUN |
| Fixed directional | `physics_v2.batched_penalty(..., corrected_mask)` | Corrected v2j checkpoints missing | NOT RUN |
| Reliability-weighted generic symmetric smoothing | `rgdr.reliability_weighted_smoothing` | None | NOT RUN |
| RGDR directional | `rgdr.rgdr_penalty` | None | NOT RUN |

The constant-reliability mathematical limit was checked against the existing fixed loss, and both generic/RGDR components have finite synthetic gradients. Their raw magnitudes differ because the generic control uses all directed edges and squares both signs; future comparisons must record train-only mean/median penalty and gradient norms and prespecify any train-only scale factor before evaluation. The binary gate removes 93–98% of the fixed directional edge instances across training/validation, so a naïve equal-λ comparison would confound directionality with regularization exposure. No claimed superiority over λ=0, fixed penalty or generic smoothing is made.
