# R00-076 — Direction correction, NOT signal replacement

**Additive continuation from verified original branch** `carson/htf-r00-073-075-original-source-continuation-20261018` at `c04aa96fd5e3818dfc36bb4b23ea84399fd733e8`.

## Non-negotiable invariant

At each original R00-065/R00-069 high-volume event timestamp and source-quote index, preserve the event and output exactly one BUY or SELL. No no-trade gate, skip, confidence suppression, event relocation, waiting for a later bar, or redesign of the established event generator. The new research problem is correcting the original side on *incorrectly classified opportunities*, not determining why already correctly classified opportunities worked. Count any damage to earlier correct directions to ensure a proposed flip actually adds net correct trades. Evaluate both sides, each broker, each UTC hour/day/week/month against the original R9 SYNTH thresholds.

All quote-reader/broker-UTC pipeline, source permissions, v1.4 research-first governance and whole-system investor laws remain authoritative and unchanged. Continue original R00-076 four-expert tick-interstitial lifecycle proposal without rebuilding the engine.

## Verified exposed diagnostic, NOT new model success

An independently SHA-reconciled local R00-076 preparation package contains original R00-069 June/July per-event same-index prediction/feature arrays. Exactly 814,244 event opportunities across two independent broker streams; baseline `repaired_065_all_volume` 366,580 correct (45.0209%).

| Previously computed side alternative | Rescued | Damaged | Neutral flips | Net |
|---|---:|---:|---:|---:|
| three_hazard_cooperative_40_40_20 | 56545 | 55776 | 15999 | +769 |
| native_context_all_volume | 70295 | 70232 | 19554 | +63 |
| first_passage_forecast_all_volume | 162301 | 163527 | 42468 | -1226 |

These are already-existing alternative direction forecasts, NOT newly discovered source alpha. Each alternative preserved the complete 814,244 original event set. June/July was historically exposed: do not use these numbers, strata or groups to choose thresholds or promote policies. The first cooperative alternative had BUY-baseline +1597 rescued net, SELL-baseline -828 net; it is an information clue only, not a source of a deployable heuristic. The fixed +30s metric labels 91,033 events neutral/missing, wrong for either side. Do not remove events or substitute a different target to improve apparent accuracy.

## Next directions (original R00-076 only; not a restart)

1. Use already-authorized original Coinexx and Dukascopy bid/ask ticks: independent expert tick-interstitial quote response transitions, opposite-side lag, spread recovery and persistence; avoid calling broker quotes actual executed flow.
2. Reuse original completed M15/H1 pivot / HH-HL / LL-LH topology and true sweep/reclaim structural phases, not slow standalone new signals.
3. Four independently reset specialists: impulse continuation, exhaustion reversal, HTF liquidity reclaim, structural pullback. Keep all original eligible events while specialists provide point-in-time direction evidence and alternate-side probability.
4. Distinct broker/session/market-regime calibrated competing UP/DOWN/NEUTRAL hazard heads; train an error-specific flip-benefit posterior rather than averaging yet another static bundle.
5. Original event index/timestamp and side remain protected until the simultaneous direction decision; corrector output must be only KEEP or FLIP, never DROP. Decisions use completed/published evidence at or before original event time.
6. January purged out-of-fold training for residual/meta labels; February policy freeze; June/July exposed transfer, strictly no policy tuning on transfer. A genuinely unseen month needs approval and registered hash.
7. Predeclare separate quote-only, HTF-only, four-specialist, cooperative and skeptical matched-volume controls with deterministic full opportunity emission. Publish each source, BUY/SELL, expert state, negative intervals and full R9 SYNTH hourly/daily/weekly/monthly event and correct quotas. No exit/P&L research.

**Sources for mechanism hypotheses only (not authorized price data):**
- Open-source state ledger: https://www.tradingview.com/script/6uptOaDX-Liquidity-Sweep-Ledger-EmpArchitect/
- Open-source body/HTF sweep confirmation: https://www.tradingview.com/script/2EdkRmfX-Market-Structure-Shift-and-CRT/
- MQL5 classifier/controller separation: https://www.mql5.com/en/articles/24161
- Community debate on fast trend/reversal switches: https://www.reddit.com/r/algotrading/comments/1x985ke/
- Scientific multihorizon LOB paper: https://doi.org/10.1111/mafi.12413 (cannot import unobserved depth/size into our bid/ask-only quotes)

**Preservation:** Local bundle `XAUUSD_R00_076_DIRECTION_CORRECTION_PREPARATION_20261018.zip`, 16,417,359 bytes, SHA256 `41045ebe5889a680df3c194e1d617f17deddad50b3eadd401a12fcafeaed7b52`, member SHA manifest/CRC checked; 12 event-level original exposed forensic NPZs and Python guard code/tests. This file is locally produced; no cloud upload claim without remote SHA readback. The linked primary GitHub branch stores source/design, but does not store large original event arrays.

**Status:** four synthetic direction preservation tests passed; no new trained R00-076 predictive model, no 80% claim, no forward-blind result, no execution/fills/P&L.
