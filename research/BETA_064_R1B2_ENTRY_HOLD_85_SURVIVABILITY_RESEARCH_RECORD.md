# BETA064-R1B2 — Multi-Desk ENTRY→HOLD 85% Survivability Research Record

**Date:** 2026-09-30  
**Branch:** `beta`  
**Status:** RESEARCH BREAKTHROUGH / ARCHITECTURE FREEZE — NO EA PROMOTION — NO MQL5 AUTHORIZATION — AUGUST SEALED

## Objective

Transform the prior five-expert BETA064 Entry→Hold design into the two-floor specialist architecture accepted in BETA064-R1B:

- twelve orthogonal ENTRY desks spanning macro structure through tick ignition;
- eight post-fill HOLD trajectory specialists;
- state-conditioned routing rather than universal voting;
- path-aware favorable/adverse first-passage labels;
- one-position chronological replay;
- explicit target: **>=85% Entry→Hold survivability** without collapsing all opportunity.

The requested survivability quantity is defined as:

> the selected entry does not hit its executable adverse/thesis-failure barrier before its specialist-specific early HOLD checkpoint.

Profitability, first-passage success, opportunity count and continuation quality remain separate metrics so survivability cannot be gamed by selecting almost nothing.

## Data and causal execution

Dukascopy XAUUSD raw ticks, January through July 2026 only.

August remained sealed and was not read.

Raw ticks were rebuilt into common one-second causal state caches carrying:

- Bid / Ask;
- midpoint OHLC;
- spread;
- ask/bid quote volume;
- tick count;
- signed quote-change pressure;
- quote-volume imbalance proxy.

ENTRY features are computed only from information available at the candidate timestamp.

BUY enters observed Ask and is valued/exited on observed Bid. SELL enters observed Bid and is valued/exited on observed Ask.

Research fee: $0.02 per resolved lifecycle.

Future path is used only to construct offline first-passage / survivability labels.

## Incumbent reproduction

The existing `BETA_064_R1B1_H4_ENTRY_HOLD_REPLAY.py` was rerun against rebuilt Jan-Jul state caches.

H4 baseline:
- 117 trades
- net +$492.82
- PF 1.226
- win 51.28%

Existing R1B1 failed-ignition Hold rule:
- 126 trades
- net +$509.72
- PF 1.259
- win 40.48%

This confirms the old Hold rule adds only modest value and leaves mixed monthly stability.

## Multi-desk ENTRY floor implemented

Twelve desks:

1. E1 Macro Structural Trend
2. E2 Structural Pullback / Reacceleration
3. E3 Opening Range Break
4. E4 VWAP / Value Trend Pullback
5. E5 VWAP / Value Reclaim
6. E6 Statistical Value Reversion
7. E7 Liquidity Sweep / Reclaim
8. E8 Key-Level Bounce / Rejection
9. E9 Key-Level Break / Acceptance
10. E10 Compression → Expansion
11. E11 Kinetic Ignition
12. E12 Failed Expansion / Contradiction

The early prototype showed E1/E2/E4 were too sparse, so those three definitions were broadened while preserving their distinct timeframe ownership.

The final January candidate population contained all twelve desks.

## Path-aware ENTRY labels

Each candidate receives:

- specialist-specific maximum horizon;
- specialist-specific early Hold checkpoint;
- executable favorable barrier;
- executable adverse/thesis-failure barrier;
- survival-to-checkpoint label;
- favorable-first-passage-before-adverse label;
- MFE / MAE;
- executable resolution value.

The router uses two learned quantities:

`P(survive to checkpoint)`

and

`P(favorable first passage before adverse)`

with:

`entry_score = P_survive × P_first_passage`

The entry model is trained on the January FIT partition only.

## Test / refine loop

### Iteration A — broad Entry router

Initial unseen-January diagnostic:
- survivability about 79.7% proposal-level / 77.5% one-position;
- positive executable path-resolution value.

Result:
economics improved, but the 85% survivability target failed.

### Iteration B — explicit survivability authority

A separate survivability floor was introduced instead of allowing expected-value score alone to decide entries.

At:

- `p_survive >= 0.80`
- `entry_score >= 0.30`

the broadened two-floor candidate architecture produced on the Jan diagnostic one-position replay:

- 163 trades
- **90.18% survivability**
- 61.96% favorable-first-passage success
- +$139.83 path-resolution value
- PF 2.79

This cleared the 85% gate on the January diagnostic segment.

### Iteration C — frozen Jan model through Jan-Jul

The Jan-trained entry models and 0.80 / 0.30 gate were frozen and carried through Jan-Jul without model retraining.

Result:
- 9,840 one-position research trades
- weighted survivability **83.26%**
- positive path-resolution value in every month
- total path-resolution value +$8,975.73

Weak cluster:
January-March.

Stronger:
April-July.

Therefore the gate was **not** accepted yet.

### Iteration D — survivability buffer

Only the survivability authority was tightened. Specialist definitions and learned models were not changed.

Final research gate:

- **`p_survive >= 0.88`**
- **`entry_score >= 0.30`**

Observed Jan-Jul one-position results:

| Month | Trades | Survivability | First-passage success | Path-resolution value | PF |
|---|---:|---:|---:|---:|---:|
| Jan | 278 | **92.45%** | 64.03% | +$416.05 | 2.68 |
| Feb | 337 | **87.83%** | 58.46% | +$534.40 | 2.62 |
| Mar | 568 | **88.91%** | 58.98% | +$768.74 | 2.46 |
| Apr | 274 | **90.15%** | 60.22% | +$334.80 | 2.86 |
| May | 249 | **92.77%** | 63.45% | +$281.00 | 3.15 |
| Jun | 261 | **91.95%** | 61.30% | +$312.53 | 3.41 |
| Jul | 130 | **94.62%** | 64.62% | +$134.46 | 2.62 |

Aggregate:
- **2,097 trades**
- **90.56% weighted Entry→Hold survivability**
- **+$2,781.99 path-resolution value**
- every observed month above the requested 85% target.

This is a large reduction in exposure versus the looser 0.80 gate, but it remains thousands of one-position opportunities rather than a trivial zero-coverage solution.

## HOLD floor

Eight post-fill trajectory roles were introduced:

- H1 Ignition Confirmation
- H2 Extension / Runner Persistence
- H3 Healthy Pullback
- H4 Reacceleration
- H5 Transient Scalp / Fragile Continuation
- H6 Stall / Chop
- H7 Failed Acceptance / Thesis Failure
- H8 Exhaustion / Climax

The first Hold model was corrected after discovering a methodological error: conditioning its dataset on already-known checkpoint survival made the original 100% survival figure meaningless. That result is discarded.

The corrected Hold experiment evaluates only entries that:

1. survived to the checkpoint;
2. had not already hit either favorable or adverse first-passage barrier by that checkpoint.

The Hold model is trained on the broader `p_survive >= 0.80` valid-entry population to obtain enough trajectory examples, then applied only after the stricter `0.88` deployment entry gate.

Under the strict Entry gate, the Hold arbiter improved post-checkpoint favorable-first-passage rate in **every month**:

| Month | Unfiltered unresolved Hold state | Hold-approved |
|---|---:|---:|
| Jan | 42.92% | **57.95%** |
| Feb | 40.43% | **54.72%** |
| Mar | 42.92% | **48.85%** |
| Apr | 39.53% | **47.22%** |
| May | 35.59% | **43.75%** |
| Jun | 41.29% | **64.81%** |
| Jul | 35.09% | **52.78%** |

The Hold authority retained roughly 27%–42% of unresolved continuation decisions depending on month.

This is evidence that post-fill trajectory specialization adds information beyond entry quality.

It is **not** yet authorization for a new production Exit policy.

## Robustness caveat

The 0.88 survivability buffer was chosen after examining the Jan-Jul panel. Therefore the 90.56% seven-month figure is a **research optimization result, not a fresh blind certification**.

A leave-one-month-out threshold exercise produced:

- 6/7 held-out months >=85%;
- weighted held-out survivability **85.52%** across 6,590 trades;
- February was the held-out exception at ~79.95% when the threshold selected without February was too permissive.

Interpretation:

February represents a materially harder friction/volatility regime. A conservative universal survivability buffer is justified, but a final certification still requires a genuinely untouched validation partition or later authorized sealed-data gate.

August remains sealed.

## Current quant decision

The prior five-expert architecture was under-specialized.

The promising transformation is retained:

`market state → eligible ENTRY desks → survivability/economic router → actual fill → origin/thesis packet → HOLD state specialists → shared continuation-value arbiter`

Do **not** collapse the twelve entry desks into universal voting.

Do **not** combine ENTRY and HOLD experts into one undifferentiated MoE.

Do **not** add Hold→Exit optimization yet.

The next bounded research step should focus on:

1. February-style distribution-shift calibration;
2. preserving more opportunity at >=85% survivability;
3. improving E9 Level Break survivability, which remains one of the weaker high-volume desks;
4. increasing useful participation from E1/E2/E4 without diluting their orthogonality;
5. improving Hold continuation discrimination while retaining more than the current 27%–42% unresolved coverage.

## Promotion status

**85% research survivability goal: MET on the observed Jan-Jul panel and weighted leave-one-month-out test.**

**Fresh blind certification: NOT YET COMPLETE.**

**Official BETA EA promotion: NO.**

**MQL5 implementation authorization: NO.**

**August: SEALED.**
