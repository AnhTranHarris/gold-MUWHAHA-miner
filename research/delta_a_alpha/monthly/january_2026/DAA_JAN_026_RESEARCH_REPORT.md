# DAA January 026 — Funded Campaign / Profit Capture / Transfer Research

**2026-10-08. Reproducible bounded research cycle.** **No accepted V1 trading modification**. August sealed, September reserved. Owner May 137 remains paused. This uses the honest incomplete January 024 V1 reconstruction; **not complete historical 131E equivalence**.

## All original assumptions retained

- Exact Jan Dukascopy raw source SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, 9,135,062 quotes. February `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`, January 10-day completed-bar warmup, no financial entry before Feb 1 UTC.
- 0.01 lot, 1 oz XAU approximate contract assumption, actual Bid/Ask at each opening/closing quote, $0.02/ticket extra fee; no slippage, swap, depth, real broker minimum stop distance, or margin and stopout model. Source 024 permits 1 physical ticket per tick and global cap; receipt-side quote/P&L reconstruction and full-tick equity mark validated for each scenario.
- Whitepaper L0–L8 and existing source2/4/5/6 route classification retained; not the exact original 049→051→075→084→119→131E funded parent chain. Reconstruction lacks certified L7 recovery execution and arbitrary-start 5-minute service level.

## Mechanism 1 — Multi-owner funded campaign cascade: FAILED

New owner-specific campaigns: 16 concurrent contexts, NY17 entry-known HTF direction and observed intraminute favorable displacement, 5-10 second start interval. First scout *physically funded*; continuation only after that particular funded child's **actual realized** profit and ≤60s hold, never shadow outcome; bounded max30 children, up to 120s per campaign, physical global cap64. Synthetic normalizing of real spreads prohibited.

- 5s, $0.25 displacement, $1.19/$1.10 quantum: 7,758 trades, +$9,901 net, gross loss -$11,333, funded cascade net -$2,510 (2,615 cascade tickets).
- Same, q >= 2× observed spread: 7,079 trades, +$11,209 net, gross loss -$10,858, cascade net -$1,203.
- Same + $4 SL: 6,896 trades, +$10,841; cascade net -$1,570.
- Stricter 10s, ≥$2 displacement, spread ≤$1.20 and q≥2×spread: 5,522 trades, +$12,307, cascade net -$104 (379 tickets).

**All** underperform unchanged January 024 control at cap64 (+$12,496.98 / 5,240 trades, gross loss -$6,098.86). Pure velocity and more parents do not solve underlying execution expectancy. Do not copy into V1.

## Mechanism 2 — Native time-exit profit locking: NOT ACCEPTED

Source6 only (original 131D named native session) per-trade actual executable max favorable movement. Test 3 activation/retracement pairs, after reaching threshold exit on first observed adverse retracement. Jan64 net +$11,799 ($3/$1.2), +$12,452 ($6/$2), +$12,381 ($10/$3). All below unchanged baseline (+$12,497). No substitution of active native lifecycle allowed.

## Mechanism 3 — Rolling funded performance capacity auction: ECONOMIC TRADE-OFF, NOT ACCEPTED

New per-native-position cap applies only after 20 truly funded source6 closed outcomes; EMA(α=.04) of realized positive/negative payoffs gives causal conditional PF estimate. Under recent PF 1.0/1.5/2.0 thresholds, soft caps 25%/25%/10% of shared physical capacity: Jan64 net +$11,840/+11,919/+11,136; trades 4,409/4,316/3,557; gross loss -$4,540/-$4,359/-$3,094. PF improves vs baseline but profit and velocity shrink. Keep performance-state fields as awareness, do NOT promote the veto.

## Mechanism 4 — Hourly high-volume harvest profit lock: JANUARY PROMISING, FEBRUARY TRANSFER FAILED

Source2 only: after **observed executable** favorable runup ≥$14, record best quote and first-close if retracement ≥$4, otherwise original target/stop/time governs. Does **not** change V1 source2 entries and creates no new unearned child. Real exit may free capacity; original funded rules still apply.

January 2026 at caps 16/64/128 versus exact same baseline without lock:

| Global cap | Baseline net | Candidate net | Δ net | Baseline trades | Candidate trades | Baseline GL | Candidate GL | Baseline full-tick DD | Candidate DD |
|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
|16|$3,848.77|$4,242.10|+$393.33|1995|2027|-$2,055.99|-$2,055.99|$452.56|$452.56|
|64|$12,496.98|$13,770.54|+$1,273.56|5240|5320|-$6,098.86|-$6,098.86|$1,761.11|$1,761.11|
|128|$20,469.05|$22,254.04|+$1,784.99|7213|7357|-$7,883.05|-$7,883.05|$3,246.53|$2,817.80|

January 64: January ISO weeks W02 +$253.67, W03 $0, W04 +$423.32, W05 +$596.57; 5 of 20 active days improved, 15 unchanged, none worse; no Jan30 uplift. This is not fully distributed daily edge. Adjacent threshold trial $12/$4 or $12/$3 also January-positive; neighborhood in-sample, not validation.

**February development transfer** using same $14/$4 settings unchanged, Jan 10-day predeployment warmup, cap64: baseline +$6,133.54 / 2,945 trades / gross loss -$3,255.33 / PF2.884 versus profitlock +$6,045.33 / 3,102 trades / gross loss -$3,908.72 / PF2.547. **Failure: net -$88.21, gross-loss deterioration $653.39.** Weekly Δ W06 -$193.53, W07 +$481.80, W08 -$376.47, W09 $0. No month name is an execution feature.

## Mechanism 5 — HTF opposition confirmation: FAILED FEBRUARY

Same $14/$4 proposal only if M5 direction opposes funded position, or combined M5/M15 opposes. On January cap64 M5 gate gives +$13,236.81, less than unconditional +$13,770.54; on February M5 gate gives +$5,697.66 versus control +$6,133.54. M5/M15 combined January identical M5 in this sample, February run timed out and is **not** represented as complete. Do not promote.

## Reconstructible literature

- MQL5 quant/restartable grid https://www.mql5.com/en/articles/21833
- MQL5 grid code patterns https://www.mql5.com/en/articles/17190 (reject dynamic lot scaling; fixed .01 mandated)
- Community cautions on grid friction https://www.reddit.com/r/algotrading/comments/1mpxpq6/
- Community validation/regime concentration https://www.reddit.com/r/algotrading/comments/1rgbu23/

## Creative next mechanism (UNTESTED): Causal Dual-Exit Selector

Preserve both original V1 and protected profits as *competing policies*. For every actual source2 signal, maintain an independently time-matured shadow record of how the untouched original time/target/stop lifecycle would exit if funded, even after a real lock exit. Only once that counterfactual would have closed, learn the incremental **policy difference** conditioned on entry-known auction state, structural HTF, quote friction and recent max-favorable/return-path state. Shadow difference can train future exit **policy selection**, never grant Watchdog paid-child credit or backfill funding. Use documented cold-start baseline and bounded gradual activation; no weeks-long waiting before normal V1 trading. Freeze before August/September. One tick first-touch and global margin remain authoritative.

**Priorities**: restore exact historical 131E parent funding and 131D coverage into raw executable engine; then test this adaptive exit-policy selector sequentially Jan→July with same rulebook and month-per-layer forensic scorecards, 100k→1k→500→300→100 margin. A January-only winning configuration is NOT a transferable edge.

Source and exact every-scenario CSV/JSON included in separate compressed tar recovery. No production EA edit or blind holdout release.