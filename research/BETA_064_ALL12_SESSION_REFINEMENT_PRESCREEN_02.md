# BETA064 — ALL-12 SESSION REFINEMENT PRESCREEN 02

**Status:** RESEARCH CHILD / NEGATIVE SESSION-SPLIT BROAD-CLOCK SCREEN — NO CHECKPOINT CHANGE

This unit follows the all-12 broad-clock prescreen and tests whether its most relevant reconstructed expansion families become portable when modeled separately by session rather than through one universal cross-session discriminator.

Frozen Major Checkpoint 02 remains immutable at 5,070 Jan–Jul trades / 88.44% weighted Entry→Hold survivability / every month >85%. August remained sealed. Alpha/GAMMA were not used. Hold→Exit remains deferred. No MQL5 change.

## Tested families

- E5 VWAP Reclaim
- E7 Sweep/Reclaim
- E10 Compression Release
- E12 Failed Expansion

Each session/specialist pair received a leave-one-month-out survival + favorable-first-passage quality model. A development threshold was admissible only when every development month retained at least three chronological one-position trades, >=85% Entry→Hold survival, and positive diagnostic value. The threshold was then applied unchanged to the omitted month.

## Result

Session splitting did not create a portable >=85% expansion stream.

Key held-out aggregates among pairs that could form any development gates:

- UK E7: 7 gated folds, only 1 held-out fold passed; 69 held-out trades, 49.28% weighted survival, negative diagnostic value.
- NY E7: 7 gated folds, 0 held-out passes; 80 held-out trades, 68.75% weighted survival, negative diagnostic value.
- NY E5: 7 gated folds, 0 held-out passes; 91 held-out trades, 61.54% weighted survival.
- UK E12: only 1 gated fold; 72.73% held-out survival and negative diagnostic value.
- NY E10: 2 gated folds; 66.67% weighted held-out survival and negative diagnostic value.
- Most E10/E12 session pairs could not form the six-month development gate at all.

The isolated UK E7 held-out pass is explicitly rejected because it occurred in only one of seven omitted-month tests and the complete gated-fold aggregate is poor.

## Scientific decision

The failure is now replicated in two structurally different screens:

1. pooled specialist broad-clock LOMO; and
2. session-split specialist LOMO.

Therefore the research should not continue optimizing these broad reconstructed clocks. Additional threshold search would increase selection bias without addressing the missing parent-candidate problem.

The supported path remains:

- keep frozen parent E1–E12 Entry clocks;
- recover opportunity through state-conditioned admission and unused/rejected parent states;
- prioritize E10/E12/E5 capacity only when exact parent-adjacent opportunity can be reconstructed;
- repair E6/E7/E9 quality using their validated parent thesis and C02G same-timestamp derivative context;
- keep E11 saturated/frozen;
- do not claim broad reconstructed clocks as checkpoint-equivalent.

## Durable artifacts

- `research/experiments/BETA_064_ALL12_SESSION_REFINEMENT_PRESCREEN_02.py`
- `research/results/BETA_064_ALL12_SESSION_REFINEMENT_PRESCREEN_02_SUMMARY.csv`

Local SHA-256 before commit:
- script: `7388c79baac53c05c32fcf0426552fc6a03468bd55baf7eacc8b0665733cdce7`
- full local fold result: `28b3235fb2175504f5d8fe207a0bea0c4cd32e34fd4daf64f846282ae468c155`
- summary: `7ab6bca6c6fa117d867c5f0e216e43f00844a54e6f48fa0d7c9d956d0b1ed7c7`

The full fold CSV is reproducible from the committed script and the pass-01 monthly candidate files.
