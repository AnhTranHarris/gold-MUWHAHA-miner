# BETA064-R1B2 — Multiscale Auction and Structural Entry-Timing Ablations

**Date:** 2026-09-30  
**Branch:** beta  
**Status:** NEGATIVE/BOUNDARY ABLATION RECORD — NO PROMOTION — AUGUST SEALED

## Context

R1B1 established a positive H4 structural Entry desk and a regime-conditioned failed-ignition Hold specialist. This unit tested two proposed ways to expand or improve that desk without using May-Jul to tune the decision.

## A. Fresh multiscale acceptance/sweep screen

The historical R10/GAMMA research had reported useful 1m/3m/5m/10m/20m boundary behavior. Because those historical economics cannot be inherited into independent BETA, the mechanism was rebuilt from current Dukascopy data.

Screening implementation:
- one-second causal cache derived from original January ticks;
- completed M1 rolling boundaries;
- scales 3m/5m/10m/20m;
- penetration +$0.05;
- reclaim buffer $0.01;
- acceptance buffer $0.05 after >=2 seconds;
- event expiry 15 seconds;
- simultaneous same-side/same-type scale events collapsed into fractal depth;
- natural action: ACCEPT follows the break, SWEEP trades the reclaim/fade;
- BUY enters Ask, SELL enters Bid, opposite quote on markout, $0.02 fee.

January partitions remained:
- FIT before Jan 9;
- CAL Jan 9-Jan 11;
- historical diagnostic Jan 11-Jan 18 12UTC.

Result: no standalone executable edge.

Representative 120-second mean utility:
- CAL ACCEPT depth>=1: about -$0.883/trade;
- CAL ACCEPT depth>=4: about -$0.959/trade;
- CAL SWEEP depth>=1: about -$1.774/trade;
- DIAG ACCEPT depth>=4: about -$0.700/trade;
- DIAG SWEEP remained substantially negative.

Conclusion:
historical multiscale boundary results do not automatically transfer into current BETA. Scale depth alone is not a viable standalone direction engine under this execution contract. Do not resurrect the old result.

The useful remnant is architectural: scale interaction can remain a **state feature** inside a specialist that already owns direction, but it is not promoted as an independent Entry desk.

## B. H4 structural pullback -> reacceleration Entry timing

Hypothesis:
keep H4 structural direction as the owner, but delay the initial fill until a lower-scale adverse retracement occurs and favorable reacceleration confirms.

The candidate Entry timing rules waited up to 60-120 minutes for combinations such as:
- 0.05 ATR pullback + 0.03 ATR reacceleration;
- 0.10 ATR pullback + 0.05 ATR reacceleration;
- 0.15 ATR pullback + 0.05/0.10 ATR reacceleration.

The already-frozen R1B1 Hold rule was retained:
- structural H4 6-bar completed breakout;
- H4 vol ratio <=2.0;
- 1.5 ATR catastrophe stop;
- +0.25 ATR trail activation;
- 1.0 ATR trail;
- 24h maximum hold;
- failed-ignition at 60m / MFE<0.10ATR / current red only when entry H4 vol ratio <=1.20.

Development/calibration comparison:

### Immediate Entry
- 146 trades
- Jan-Jul +$766.37
- PF 1.532
- Jan-Mar + April sum +$512.67
- development/calibration monthly floor -$16.48

### 0.05 ATR pullback + 0.03 ATR reacceleration, max wait 60m
- 136 trades
- Jan-Jul +$694.47
- PF 1.469
- Jan-Mar + April sum +$446.47
- development/calibration monthly floor -$13.02

This slightly improves the worst month but lowers total development/calibration value and full-period value.

Deeper waits:
- reduced trade count;
- generally weakened Jan-Apr;
- some looked stronger in May-Jul, but May-Jul had already been inspected and therefore cannot be used to choose the timing rule.

Decision:
**retain immediate H4 structural entry. Reject delayed pullback/reacceleration as the default H4 Entry mechanism.**

This is an important separation-of-jobs result:
- for the H4 desk, the completed structural breakout already carries the useful entry information;
- the larger improvement came from **post-fill Hold state ownership**, not micro-timing the initial fill.

## Current survivor set

At the end of R1B2:

1. **ENTRY survivor: H4_STRUCTURAL**
2. **HOLD survivor A: FAILED_IGNITION_NORMAL_VOL**
3. **HOLD survivor B: SLOW_IGNITION_HIGH_VOL**
4. H1 structural: pruned under current BETA execution.
5. Generic 12-desk prototypes: no calibration survivor.
6. Standalone multiscale acceptance/sweep: rejected.
7. H4 delayed pullback/reacceleration entry: rejected as default.

The next useful search should add an orthogonal Entry desk with a different economic mechanism, not another timing variation around H4.

No MQL5 authorization. August remains SEALED.
