# BETA064-R1A — Entry→Hold Ceiling and Specialist Deficiency Diagnostic

**Date:** 2026-09-30  
**Branch:** `beta`  
**Status:** BOUNDED DIAGNOSTIC FAILURE — NO PROMOTION — NO MQL5 AUTHORIZATION — AUGUST SEALED

## Purpose

This unit executed a sequence of bounded Dukascopy January probes to determine whether the BETA064 Entry→Hold expert pool contains enough executable directional value to justify immediate counterfactual-regret router optimization.

It does **not** replace the formal BETA064 lifecycle replay. These probes intentionally isolate directional/event-clock economics before the full router, online trust, continuation policy, or Hold→Exit phase.

Source: original January 2026 Dukascopy XAUUSD tick CSV.GZ already used by the BETA campaign.

Historical partitions preserved:
- FIT: Jan 1–Jan 9
- CAL: Jan 9–Jan 11
- DIAGNOSTIC: Jan 11–Jan 18 12UTC
- August untouched / SEALED

All execution-value probes used observed Ask for BUY entry, observed Bid for SELL entry, opposite quote on close, and $0.02 round-trip fee. Same-source chronological ordering was preserved. Several early probes used 1-second causal event snapshots as a computational preflight; therefore they are diagnostic, not final BETA064 parity.

## Probe 1 — continuous 1-second heterogeneous expert ceiling

Five heterogeneous prototype experts were tested on 15s/30s executable utility:
- trend linear/sequence proxy,
- nonlinear structural tree,
- nonlinear sweep expert,
- deterministic V8-like auction FSM proxy,
- nonlinear transition precursor.

Diagnostic Jan11–Jan18:
- expert-action hindsight oracle: **+$19,758.13** over the overlapping diagnostic event set;
- deployable fixed predicted-value router: **−$128,516.34**;
- calibrated WAIT/margin router: **−$55,492.86**;
- the oracle positive subset was dominated by the deterministic auction proxy.

Interpretation:
the event population contains profitable future paths, but the deployed models cannot identify them reliably. The oracle result is non-deployable and must not be reported as strategy alpha.

## Probe 2 — classification objective instead of mean-value regression

The target was changed from expected utility regression to probability of positive executable utility.

Result:
high-confidence subsets increased hit rate but remained negative on the CAL window. Therefore the original failure was not repaired by switching loss functions. Magnitude of adverse outcomes still dominated.

## Probe 3 — sparse state-change specialist rules

Six sparse state families were tested with calibration-selected score thresholds and deterministic time deduplication:
- IGNITION,
- RETRACE,
- SWEEP,
- COMPRESSION,
- TRANSITION,
- RANGE_FSM.

Every family remained negative on CAL and diagnostic in its nominal direction. Explicit direction inversion was also tested and did not repair expectancy.

Diagnostic union:
- sparse-family hindsight oracle: approximately **+$1,203**;
- simple deployable family router: approximately **−$6,280**.

Again the gap is identification, not absence of all favorable paths.

## Probe 4 — hold-horizon scan

Nominal and inverted specialist directions were evaluated from 1s through 90s.

Result:
mean executable utility stayed broadly negative across the full horizon range. Extending the fixed hold did not remove the loss.

The empirical loss level was close to the contemporaneous spread burden, suggesting the specialists were not forecasting enough directional displacement to amortize entry/exit friction.

## Probe 5 — low-spread and longer structural holds

Range/sweep-style states were filtered by increasingly narrow current spread and extended through 30/60/90/120/180/300 seconds.

No stable positive expectancy appeared, including in the low-spread subsets with adequate sample size.

Conclusion:
a simple friction gate cannot manufacture the missing directional edge.

## Probe 6 — new micro-liquidity / quote-volume specialist

A genuinely new specialist was added from Dukascopy tick fields:
- bid/ask quote volume imbalance,
- imbalance change,
- quote-direction counts,
- tick intensity,
- spread compression,
- short-horizon returns.

Dukascopy documentation confirms the files contain ask and bid quote volumes; these were treated as quote-side volume/depth-like state only, **not** as aggressor trade flow.

The high-score calibration subset remained economically negative. This specialist did not bridge the gap.

## Probe 7 — direction versus cost decomposition

A nonlinear 30-second direction model was trained on short-horizon price, volatility, quote imbalance, tick-intensity and spread state.

Diagnostic selected events:
- gross midpoint directional edge: approximately **+$0.096/oz per event**;
- executable net edge: approximately **−$0.773/oz per event**;
- median diagnostic spread: approximately **$0.677/oz**;
- mean diagnostic spread: approximately **$0.690/oz**.

This is the clearest current diagnosis: **some directional information exists, but its magnitude is far too small to pay executable friction at the tested horizon.**

## Probe 8 — 2–10 minute directional extension

The directional target was extended to 120/180/300/600 seconds.

The 600-second model looked positive on CAL:
- overlapping CAL selected-event mean net: approximately +$0.319.

It failed badly on the later diagnostic window:
- overlapping diagnostic selected-event mean net: approximately −$0.774.

This exposed strong within-January instability / regime shift rather than a stable longer-horizon alpha.

## Probe 9 — one-position chronological replay and causal trust

The 30s and 600s streams were replayed with one real position at a time.

600-second CAL:
- 93 positions,
- net **+$19.54**,
- mean +$0.210.

600-second Jan11–Jan18 diagnostic:
- 508 positions,
- net **−$357.95**,
- mean −$0.705,
- win rate 43.70%.

A causal EWMA shadow-trust gate, updated only after shadow outcomes became observable, still lost:
- 299 positions,
- net **−$217.56**.

Therefore immediate online trust does not rescue the unstable directional model.

## Probe 10 — new macro-structure specialist

A second materially different specialist was added using:
- 5s/15s/30s/1m/2m/5m/10m/15m/30m/60m returns,
- multi-scale efficiency,
- 1m/5m/15m/30m volatility,
- multi-scale range location,
- spread state,
- session state.

600-second one-position CAL:
- 113 positions,
- net **+$50.28**,
- mean +$0.445,
- win rate 54.87%.

Jan11–Jan18 diagnostic:
- 607 positions,
- net **−$431.75**,
- mean −$0.711,
- win rate 43.00%.

Every observed diagnostic day Jan11–Jan16 was negative.

Conclusion:
the missing gap is **not simply lack of higher-timeframe context**.

## Current diagnosis

The current BETA064 Entry→Hold failure is now more narrowly localized:

1. **Executable directional displacement is too small** relative to spread for the tested 15–90s high-frequency states.
2. Longer 2–10 minute models can look positive on the short CAL slice but **do not persist** into the Jan diagnostic period.
3. Adding a quote-volume/liquidity specialist and a macro-structure specialist did **not** create stable post-cost alpha.
4. Explicit side inversion did not repair the specialist families.
5. WAIT/confidence thresholds and simple causal online trust reduce exposure but do not create positive expectancy.
6. The expert-pool hindsight oracle remains materially above the deployable router, so profitable future paths exist; however present causal state features do not identify them with sufficient reliability.
7. Immediate router optimization is therefore premature. The next target should change the **economic label/lifecycle**, not merely the router.

## Next materially different experiment

### BETA064-R1B — Path-aware first-passage Entry→Hold target

Replace fixed-horizon markout labels with causal-training labels derived from the **future path** while preserving causal runtime features.

For each candidate entry state and side, calculate in TRAIN labels only:
- time to favorable excursion thresholds;
- time to adverse excursion thresholds;
- first-passage winner: favorable excursion before adverse excursion;
- maximum favorable/adverse excursion before horizon;
- executable value at bounded continuation ages;
- probability/value of surviving to 1s/3s/5s/10s/30s/60s/120s;
- residual value conditional on survival.

The label may inspect future training path; runtime features may not.

Candidate experts should predict:
- probability favorable barrier is hit before adverse barrier,
- expected first-passage time,
- conditional continuation value,
- tail loss.

This directly matches the intended Entry→Hold question:
**not “where is price exactly N seconds later?” but “does this entry reach economically useful favorable territory before the trade becomes structurally invalid?”**

Use original tick chronology for barrier ordering on shortlisted events; 250ms aggregates may be used only as a screening cache when exact same-bucket ordering is not needed.

No Hold→Exit optimization is authorized: first-passage labels are used to improve ENTRY and HOLD-worthiness, not to design a new production exit policy.

## Decision

**NO BETA064 promotion.**  
**NO MQL5.**  
**NO August access.**  
**Do not add additional near-duplicate specialists until R1B proves the path-aware target contains stable causal signal.**

If R1B still fails, the research program should reconsider whether this Dukascopy feed supports the requested high-frequency economics under observed spread, rather than increasing model complexity.
