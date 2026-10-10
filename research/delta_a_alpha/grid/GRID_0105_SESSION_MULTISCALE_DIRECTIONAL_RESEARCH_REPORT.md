# GRID-0105 — Grid-native directional mechanism synthesis with session clocks and completed tick-to-daily bars

**Research date:** 2026-10-10. **Status: Research complete / economically negative / NO trading mechanism promoted.**

## Owner scope and science walls
The current research seeks a creator-grid-derived, high-volume XAUUSD opportunity generator with *correct initial direction*, using session clocks and causal tick/second/minute/hour/daily-candle features **before** activating L3-L7 of the full Vertical Grid. $100,000 is the *future research-account* assumption; this experiment produces **zero funded trades, zero positions, zero portfolio P/L**. R9 Gamma HybridGate SYNTH is the eventual performance and velocity target, **not** a correct-direction oracle. No Martingale lot multiplier, automatic adverse averaging, or source-control resurrection of deleted Jan/Feb engines.

Data: original **read-only Dukascopy CSV.gz** files (price raw scale 1000, Bid and Ask separate). January **9,135,062 ticks**; February **7,538,339**; April **7,470,570**. Original SHA-256: January `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`, February `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5`, April `30375098f62aed6cabc32ec6b67c57c20baec9b6d9be1ce0a204e09806c1ec0f`. No altered or invented execution overlay was substituted for original quotes.

The preserved GRID0104 nontrading generator yielded the same **54,210 January**, **60,603 February**, and **53,569 April** causal raw virtual crossing events at **$0.75 per rung / 15 seconds deduplication**. These are not trade executions or guaranteed unique profitable opportunities. Approximate session/day counts depend on broker reporting clock, DST, and whether tick quote availability is sufficient. Observed quote revisions are **not** an exchange-wide trade tape or authenticated aggressive order-flow volume.

## Source-based creative synthesis
Public reproducible influences studied, NOT imported as black-box alpha:

- [MQL5 Intrinsic Time / Directional-Change Scaling Laws](https://www.mql5.com/en/articles/23814): finite state `last extreme -> confirmed directional change -> overshoot`, event-rate scaling, with a vital lookahead rule: **an overshoot cannot be labeled complete until later reversal**. Its particular live EA inventory/cascade profitability is **not assumed or imported**.
- [MQL5 Activity and Imbalance Bars in Python/MQL5](https://www.mql5.com/en/articles/22063): event-driven bar counts and signed tick proxy, with explicit caveat that quote-price changes are only an estimate of true trade aggressor volume.
- [MQL5 Microstructure Order Flow](https://www.mql5.com/en/articles/22939), [Microstructure Noise](https://www.mql5.com/en/articles/22938): completed-candle close-location and quote-path noise, avoiding the false statement that Dukascopy quote updates are actual traded order-flow records.
- [MQL5 regime-aware constrained grid](https://www.mql5.com/en/articles/21833): bounded event cycles and inventory constraints, not a warrant to use Martingale or extrapolate EURUSD/US500 performance to XAUUSD.

New clean-room hypothesis families: virtual rung genealogy, tick-path efficiency (net displacement / absolute traversed tick path), quote update intensity and spread changes, online directional-change event state at 0.75/1.50/3.00 dollars, completed 1s/5s/15s/M1/M5/M15/H1/D1 candle bodies and close locations, and four venue-local DST-correct session clocks. These are entry-known **opportunity descriptors**, not independent funded trading sleeves. The structural roles are still *features*, not the finalized owner L1–L7 trading-quality architecture.

### Causality and terminology
Every candle feature uses a **previously completed** bar. Tick features use historical quote snapshots only. Label outcomes are calculated *later*, offline, not passed into admission logic. A hypothetical entry is assessed on the first original quote at or after a **250 ms** delivery delay; the fixed 60/120/300/600-second diagnostic horizon uses a future quote side and subtracts a hypothetical **$0.02** per 0.01 lot in round-trip commission. This is **not** an actual order-fill simulator; no rejected orders, margin, order queues, latency distribution, real exit mechanics, or managed stops are modeled. Therefore mean fixed-horizon values are **shadow markouts** in dollar-equivalent units, not broker-proven trade P/L.

An implementation terminology correction: the tested feature previously labeled `dc_overshoot_*` is **only the most recent tick price change divided by DC threshold**, not an authentic completed directional-change overshoot. The shipped source renames it `dc_last_tick_move_*` without changing trained feature values or order. **Real-time completed DC overshoot characteristics remain untested.** This prevents promotion of a mechanism we did not implement.

## Chronological scientific partition
- **January 1–15 UTC:** training and fitting only (linear ridge, shallow HistGradientBoosting).
- **January 16–31 UTC:** same-month historical validation.
- **February whole month:** independent cross-month challenge, without refitting.
- **April whole month:** first evaluation of two January+February-frozen models. This was a genuine separately frozen first family check. A **subsequent** rule-ablation study reused April as a *secondary exploratory check*; because its broad results had already been viewed, do **not** describe April as untouched for this second study. A different never-seen month is needed before future strong claims.

The nonlinear model uses at most eight leaves, 85 boosting passes, min leaf 400, regularization 200. Ridge alpha 3000, standardization fitted only on first-half January. Both are lightweight hypothesis approximations, not guarantees of AI alpha. **32 fitted model/threshold variants**, **24 naive baseline direction/horizon variants**, **192 handcrafted multi-timeframe/DC/spread rules** screened. All alternatives share underlying grid quotes; multiplying configuration counts does not create more independent samples. Repeated comparisons invite false discovery; require independent day-level consistency.

## Results — frozen regression models

| Model | Horizon | Jan16–31 mean | Feb mean | April frozen OOS mean | April quote-side positive | April selected events |
|---|---:|---:|---:|---:|---:|---:|
| Nonlinear shallow histogram boosting | 120s | **−$0.9882** | **−$0.9676** | **−$0.7462** | 38.349% | 53,420 |
| Regularized ridge | 300s | **−$1.0185** | **−$0.9644** | **−$0.7001** | 42.909% | 53,350 |

Both frozen models issue non-abstaining directional predictions on nearly every eligible grid event. They preserve *raw* event throughput but FAIL economic directional quality; April day means were negative on **all 25 quoted UTC days** for both models. No profitable condition is promoted.

## Results — independent alternative mechanical proposals
192 predeclared policy variants (grid-reversion/continuation; recent 15/60/300sec tick direction; last completed M1/M5/H1 body alignment; multi-timescale body consistency; directional-change phase; current spread; grid depth) were compared on Jan16–31 and whole February with 120/300s quote-side outcomes, **not** optimized for net account gains. Every policy with at least 500 eligible January validation events and at least 500 February events had a *negative mean* on at least one; the top-by-worst-month cases were also negative in both.

| Frozen Jan/Feb rule | Jan16–31 eligible | Feb eligible | Worst Jan/Feb average | April secondary mean |
|---|---:|---:|---:|---:|
| Grid reversal; source spread ≤ $1; 300s evaluation | 25,348 | 40,708 | **−$0.7799** | **−$0.6858** |
| DC(0.75)/DC(1.5) phase agree; spread ≤ $1; 120s | 16,970 | 28,061 | **−$0.8224** | **−$0.8172** |
| Grid continuation; spread ≤ $1; 120s | 25,376 | 40,771 | **−$0.8356** | **−$0.7761** |

None reaches high-probability after-cost initial direction. The first rule retained 95.21% of all evaluated April raw events but won on only 42.983% of hypothetical quote-side outcomes. This is high-volume **bad-quality** information, not viable trading.

## The tempting but forbidden hindsight ceiling

If a non-causal oracle can CHOOSE BUY or SELL after viewing the future 300s closing quotes, the best of two hypothetical quote-side outcomes is positive for January **84.494%**, February **85.146%**, April **83.719%** of eligible observed grid events. Median aggregate two-sided spread costs were about $1.38, $1.71, and $1.42 respectively. **This is prohibited for actual signal generation**. It describes how often one hindsight direction would have succeeded, not whether a causal model can choose it and not whether a realistic managed strategy would survive. Oracle net/drawdown may not be claimed. The large gap between ~84% future potential and ~39–43% realized April fixed-horizon directional correctness is the central scientific obstacle.

## Decisions and next creative cycle
**RETAIN:** virtual price-rung clock; causal quote tick cadence; multiple completed clocks and sessions as observable contexts; 250ms delayed Bid/Ask markout audit; real future-unknown direction/abstain and confidence scoring; clean daily block replication.

**REJECT for promotion:** grid reversal/continuation alone, completed timeframe votes alone, simple DC phase alignment, this particular 105-feature nonlinear or ridge predictor, event flood as a trade count, April hindsight routing, adjusted high win-rate without quote equity, no-stop physical grid, and any Martingale lot or basket loss acceleration. $100K discovery capital changes future funding feasibility, not these negative results.

**Priority research questions before unlocking owner L3–L7:**
1. Model a **competing-risks first-passage hazard** for executable +/- move, conditioned on quote age and *true* completed DC overshoot, rather than infer direction from fixed-terminal returns alone. Censor events with no observed barrier and evaluate calibration Brier/log-loss and direction-specific economic value, not just label accuracy.
2. Build an **event-state lattice with renewal/debounce**: distinguish first level, failed continuation, reclaim, skipped level jumps, first actual return, and structural break; avoid fake opportunities from repeated price oscillation. Event definitions must be time-stamped at confirmation, never backdated.
3. Test **longer-lasting opportunities relative to native spread**, online quantiles of event duration vs spread/volatility, and explicitly accept abstention when costs exceed achievable displacement. Test event-generation diversity independently from direction accuracy.
4. Distinguish broker **Coinexx** historically calibrated friction from raw **Dukascopy** bid/ask. Any modeled Coinexx-like overlay must remain separately labeled and causal; do not silently overwrite Dukascopy quotes to make a hypothesis win.
5. Evaluate truly never-seen additional months after Jan/Feb/April exploratory uses. Only when high-direction reliability survives independent data should we ratify four separate session-specific grid self-adjustment mechanisms or turn L3–L7 into funded positions.

**Acceptance:** This unit does **not** meet R9 SYNTH-level daily qualified opportunity floor, high directional accuracy, profitability/PF, or latency-stressed funded account consistency. Only candidate event throughput has been demonstrated.

## Reproduction and integrity
Artifacts: `grid0105_causal_session_multiscale.py`, `grid0105_mechanism_ablation.py`, `grid0105_april_oos_frozen.py`, `grid0105_gate_april_frozen.py`, `grid0105_oracle_ceiling_diagnostics.py`, `pre_session_cycle0104.py`, `grid_event_research.py`, `test_grid0105_contracts.py`, trained Jan-only `.joblib` models, frozen selection JSON and full date-scoped results. **9/9 new deterministic tests pass**; earlier GRID0104 12/12 owner tests were not rerun as part of this claim. The archive contains NO source-market data and does NOT mutate user originals.


## Exact source/model archive
Original Python source, deterministic 9 tests, frozen training artifacts, Jan/Feb results, April checks and the independently labeled future-aware oracle are preserved in the [GRID0105 source archive](https://drive.google.com/file/d/1PE7xmkvLLMJmmslzxBk7vkT6xBg-88K7/view), SHA256 `b528dbe629e0cad8a5285e75fe780222687eae0c94a7b54b857b4848b0f866d3`. Do not turn this negative research outcome into an accepted grid trading policy. The physical/real-time execution path remains unchanged.
