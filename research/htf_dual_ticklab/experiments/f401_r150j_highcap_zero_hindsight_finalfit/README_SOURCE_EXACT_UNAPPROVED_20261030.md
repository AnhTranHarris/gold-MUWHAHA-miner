# F401-R150J — high-capacity four-month hindsight-supervised / zero-hindsight-input final-fit continuation

**Status:** RESEARCH ONLY / UNAPPROVED.  
**Direct parent:** F401-R150I source-pilot HEAD `170a79abb676e631db228f5b2ea4c687e03c0140`.  
**Why R150J:** the active MT5_EXPAND ledger already contains R150I as a separate lower-capacity 60k-fit-per-broker pilot. This materially different high-capacity successor preserves that negative control unchanged.

## Owner methodology correction implemented

Historical Jan/Feb/Jun/Jul FILTER08 hindsight is used as **offline teacher/target only**. Runtime receives **zero hindsight input**. This is deliberately not described as “teacher-free training.”

The checklist function/model is judged against the function/model it replaces. The whole FILTER collection, not one R150J head, is later judged against the 71% CORRECT-retention / 90% wrong-rejection per-cell system gate.

## Zero-hindsight foresight bank

252D source-market state at genuine T1:
- R120 92D: 250ms/500ms/1s/5s/15s/30s causal micro/session/grid state.
- R120 36D: completed M1/M5/M15/H1 state.
- R147 57D: strict t0-to-T1 source path.
- R150E 20D: source-only cross-scale interaction block.
- R150F2 23D: first genuine t0+[15,16)s quote-prefix state; absolute tape index removed.
- R150F3U 24D: Jeffreys Beta-binomial quote reliability/path interactions.

Runtime blacklist: historical truth, teacher score/rank/mask, matured outcome-class state/rates, R24 outputs, R148B outputs/monitor, R150G parent scores, sampled-event BOCPD8, future physical outcome.

All eight authorized Coinexx/Dukascopy Jan/Feb/Jun/Jul raw files were freshly SHA-256 rehashed and matched the frozen registry before feature construction.

## Training

Per broker: deterministic 400,000-row four-month training sample = 100,000 valid rows/month. High-capacity XGBoost bank:
- historical teacher selected-mask student;
- continuous within-cell teacher-rank student;
- CORRECT specialist;
- OPPOSITE specialist;
- NEUTRAL specialist.

Hyperparameter selection used chronological FIT/CAL only; TEST was diagnostic. D12 produced only marginal CAL improvement and exceeded bounded full-fit compute; D8 was within 0.0015 teacher-mask CAL AUC on both brokers and was retained under the fail-fast/resource rule.

## Full-cell fitted diagnostics

CORRECT-class AUC, Coinexx Jan/Feb/Jun/Jul:
`0.82147 / 0.82917 / 0.83506 / 0.83196`.

CORRECT-class AUC, Dukascopy Jan/Feb/Jun/Jul:
`0.81979 / 0.82686 / 0.83489 / 0.82939`.

Runtime mutation proof: on each broker, 2,048 genuine January vectors were scored, then truth, continuous teacher score and teacher mask arrays were arbitrarily mutated. Teacher-mask student, teacher-rank student and all class-specialist outputs were bit-identical.

## Current M-DK-01 replacement comparison

Historical Dukascopy January teacher benchmark: **94,603 wrong veto / 7 CORRECT lost**.

R150J strict market-only loss-matched best current score at <=7 CORRECT losses: **1,016 wrong veto / 7 CORRECT lost**, split 990 OPPOSITE + 26 NEUTRAL.

Therefore **M-DK-01 remains OPEN**. This initial high-capacity strict-market-only fit has genuine selectivity but does not reproduce the historical teacher's volume.

## Evidence

A full 42-member code/model/eight-cell-score package was created with CRC PASS and member SHA manifest PASS. Corrected R150J local package:
`F401_R150J_FOUR_MONTH_ZERO_HINDSIGHT_INFERENCE_OFFLINE_TEACHER_HIGHCAP_TRAIN_UNAPPROVED.zip`
SHA-256 `e73ba850b6ec7a82286661cd699bc1db71c2aca1af03902c004010e9d3d1d712`.

Corrected R150J scientific receipt SHA-256:
`54f65146f692a349ff8f9001a5e727867d5f1cfe812cd9568874a0be4148fe94`.

Before the latest ledger R150I collision was discovered, the same scientific run was uploaded to MT5_EXPAND under an R150I filename. Those bytes are preserved as an immutable naming-error precursor and must not be confused with the ledger's earlier R150I source-pilot. The active research identity is R150J.

No /02 promotion, no checklist self-approval, no G07/G08/G09, no OrderSend, no P&L/profitability claim.
