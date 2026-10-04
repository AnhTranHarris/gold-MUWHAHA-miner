# DELTA R037 — Quote Propagation Leader/Follower — Checkpoint 17BA

**Status:** COMPLETE / NO EXECUTABLE SURVIVOR / RETIRED  
**Parent:** R037_TSO_STAGE_A_SCREEN_CHECKPOINT_17AZ  
**Surface:** native Dukascopy BBO signal / Coinexx-like P75 execution  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Research question

Can a sparse two-step FX quote-propagation event preserve enough residual directional information after both BBO sides have repriced to survive the frozen 30-second P75 execution lifecycle?

The source-grounded event was preregistered before compute:

- bullish: ask increases with bid unchanged, then the **next BBO price-changing event** is bid increase with ask unchanged;
- bearish: bid decreases with ask unchanged, then the next BBO price-changing event is ask decrease with bid unchanged;
- the follower spread must be no wider than the spread immediately before the leader;
- entry occurs on the first strictly subsequent raw tick.

This tests quote-side information propagation, not the already-retired one-sided-spread-shock mean-reversion family.

## Source basis

The family is based on public, reconstructible FX microstructure observations that quote revisions carry information, that revisions on one side can influence later pricing, and that bid/ask best prices are dynamically linked through spread adjustment.

No volume imbalance, fitted thresholds, session filters, side filters, timing-window search, or exit retuning were permitted.

## Integrity

- prereg commit: `ee771014b206b3e1a9f77777bfaf46b662168461`
- producer commit: `e40480d6ca6d004daf032831524ac3d068a301ed`
- producer blob: `6412fff9ee24d3f40638c7b09e1099d046c17592`
- producer SHA-256: `e7302c93d626f7212d5f1fe400c8f3fcdd210635faf7177dafda3642a04ef86e`
- canonical January SHA: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**
- official raw result SHA-256: `62378ab24fa02e49d37e51206f3e1f664a8b37ce6290b0a3f26e429c342e5e43`
- exact local Git blob = committed GitHub blob: **PASS**
- Python compilation: **PASS**
- hard process timeout: **120 s**
- atomic result output: **PASS**

An earlier local scratch reconstruction had a different Git blob. Its result was rejected before persistence. The official run was repeated only after the exact committed bytes reproduced blob `6412fff9...`.

## Stage-A result

- native price-changing BBO events: **4,205,648**
- completed same-direction leader/follower pairs before spread-restore gate: **49,447**
- restored-spread signals: **25,182**
- executable trades: **16,910**
- distinct days: **14**
- long / short: **8,428 / 8,482**
- official wins: **7,665**
- gross profit: **+$1,610.11**
- gross loss: **-$5,073.49**
- direct net: **-$3,632.48**
- exits: **16,348 STOP / 562 MAX_HOLD**

## Predictive fingerprint

The pattern has only weak residual information after follower confirmation:

- next nonzero mid move: **51.99%**
- 250 ms: **51.38%**
- 1 s: **50.82%**
- 5 s: **50.43%**

Median leader-to-follower latency is **101 ms**. The information has largely dissipated by the time both sides have repriced and spread has restored.

## Decision

**RETIRE_QPLF_STAGE_A_NO_EXECUTABLE_SURVIVOR.**

Do not rescue with:
- leader/follower size thresholds;
- latency thresholds;
- session/side/weekday filters;
- QIM/OFI overlays;
- spread percentile filters;
- exit retuning.

The family supplied a clean falsification: quote-side propagation is real enough to measure but too weak and too dense after confirmation to overcome P75 execution.

**Next:** `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`
