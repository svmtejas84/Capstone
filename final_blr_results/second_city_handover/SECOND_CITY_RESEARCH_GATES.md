# Research gates

**Gate 0: eligibility.** Source-level hourly inventory, instrument comparability, station count, operating duration, spatial coverage, license, weather alignment. Fail => no training.

**Gate 1: protocol.** Supervisor approves frozen forecast-time information set, spatial and temporal split, baselines, physical quantities, statistical family, and resource limits.

**Gate 2: reproducibility.** Pin hashes, environment, transforms, code and backup; dry-run data audit without test-score access.

**Gate 3: bounded pilot.** Only after explicit training authorization; measure runtime and VRAM, validation-only debugging, restart-safe checkpoints.

**Gate 4: locked evaluation.** One untouched external-city test; independent-site analysis and multiplicity plan; preserve negative outcomes.

**Gate 5: claims.** Predictive performance, physics validity, spatial transfer, road estimates, and routing each require separate evidence. No gate implies another.
