# DELTA R037 — RSI2 Trend-Aligned Mean-Reversion Stage-A Screen — Checkpoint 17C

**Status:** COMPLETE / NO SCREEN SURVIVOR / FAMILY RETIRED  
**Family:** R037-RSI2-v1  
**Parent:** R037_DCB_STAGE_A_SCREEN_CHECKPOINT_17B  
**Surface:** DUKAS_COINEXX_LIKE_P75 / Stage-A  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Frozen source hypothesis

MetaQuotes publishes a Connors-style RSI2 mean-reversion grammar using completed-bar RSI(2) extremes with a 200-period moving-average trend filter. A second published pullback variant requires three consecutive extreme RSI2 observations. This unit froze those two grammars on M1 and M5 before compute and retained the existing DELTA parent-priority scheduler and 30-second initial-hold execution unchanged.

No RSI period, threshold, SMA length, timeframe, session, long/short split, or exit was tuned after the result.

## Crash-safe official compute

- prereg + producer commit: `a292a57c6f5b946c450c9ebc8a3703e89e183bd1`
- producer blob: `b521ff0b7c7273d8421cdfc262eb4d81c287c33a`
- producer SHA-256: `2dce5517cf885ebd071a77f5a91a50c33012269a45f685ba9951ace82f6b8577`
- CI/recovery run: **37175391190 PASS**
- recovery artifact: **11293305615**
- canonical January SHA-256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`
- Stage-A ticks: **4,205,709**
- bounded runner: **27.188 seconds / exit 0**
- official raw result SHA-256: `53785e62d6364dca84201404c573db75ec795c58bfa8d7a1b4b27ace4c653dc5`

## Results

Parent: **14,034 trades / 6,349 official wins / -$2,944.94 net**.

- **C01 M1 classic:** 614 proposals, 580 accepted; +565 trades / +219 wins / **-$154.26 net delta**; direct RSI2 net **-$149.85**; equity-DD +5.24%.
- **C02 M1 three-extreme pullback:** 271 proposals, 254 accepted; +247 / +100 / **-$65.71**; direct **-$65.99**; equity-DD +2.23%.
- **C03 M5 classic:** 102 proposals, 98 accepted; +97 / +44 / **-$21.09**; direct **-$23.93**; equity-DD +0.72%.
- **C04 M5 three-extreme pullback:** 45 proposals, 44 accepted; +44 / +20 / **-$9.63**; direct **-$11.56**; equity-DD +0.33%.

No configuration met the frozen -$2 net gate, so none reached ordinary or strong screen pass.

## Interpretation

Increasing timeframe and demanding persistent exhaustion steadily reduced damage, but the sign never turned positive. Under the frozen 30-second initial-hold contract, RSI2 exhaustion identifies events but does not time the immediate reversal tightly enough. The failure is therefore useful: **do not spend cycles tuning RSI thresholds or MA lengths inside this family.**

## Decision

**Checkpoint 17C = NO SCREEN SURVIVOR. RETIRE R037-RSI2-v1 from the active promotion path.**

Next: `R037_NEXT_INDEPENDENT_ENTRY_SOURCE_HARVEST`.

The next family should emphasize an actual **causal reversal/impulse transition**, not merely an extreme oscillator state, while remaining independent of session opening ranges, previous-day sweeps, VCE compression and Donchian continuation.
