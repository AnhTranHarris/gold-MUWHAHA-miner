# BETA 018 — Owner mandate: entry-first R9-teacher research and blind validation

**Status:** RESEARCH PRIORITY AND EXPERIMENT PROTOCOL ONLY. No new strategy result, no MQL5 coding authorization, no accepted BETA EA, and no change to the BETA 015 owner-locked risk profile. Applies solely to the existing independent `beta` research lineage. Owner directive: prioritize **ENTRY accuracy** until a demonstrable, desirable causal level is achieved; then, only by a subsequent owner direction, increase attention to **HOLD** and **EXIT**.

## 1. The correct interpretation of the R9 targets

- **Historical R9 SYNTH (MT5 "Every tick")** is a strong *aspirational, modeled-path example* of entry / hold / exit behavior and an offline hypothesis teacher. Its generated intra-minute tick trajectory is not a verified executable profit opportunity on actual quotes. Never claim R9 SYNTH entry events, fill prices, precision, or +P&L are ground truth for Dukascopy raw ticks.
- **R9 OVERFIT / hindsight teacher** is permitted to identify *retrospective* setups worth studying. It is not an executable policy. Keep all future-path labels, MFE, MAE, and optimal-entry annotations in teacher/evaluation data only; never expose them to features, thresholds evaluated on the same future period, event approval, order selection, stops, or router action.
- **Historical R9 REAL** is a Coinexx broker-real-tick reference for where the original EA *actually traded in its tester*. Coinexx R9 REAL and Dukascopy are distinct feeds; direct tick-by-tick timestamp/quote/entry matching requires independent source-specific matching tolerance and compatible timestamps, not assumed row-by-row parity.
- **Same-feed causally executable BETA candidate on original Dukascopy ordered Bid/Ask quotes** is the research authority for entry accuracy. The owner-run Coinexx MT5 M1 "Every tick based on real ticks" test and explicit owner acceptance remain mandatory before treating a candidate as an approved EA baseline.
- Aim to approximate **the quality of opportunities implied by R9's teacher** under real Bid/Ask conditions, **not blindly copy the synthetic entry count**. Distinct datasets and synthetic ticks may not share the same event boundaries.

## 2. Research priority and experimental freeze

**PRIMARY: ENTRY.** Retain the primary owner's nonnumeric priority `ENTRY >> HOLD, EXIT`, measured on the same legitimate opportunity population. Do not invent an owner-approved 70/20/10 weighting or a winner threshold not explicitly designated by owner. Research changes must chiefly affect eligibility, direction, signal timing, or single-account routing.

**FROZEN CONTROLS (initial entry-isolation studies):** retain comparable R9-style hold/exit geometry ($0.30 gold-price stop, $0.10 trail activation, $0.03 trail gap, up to 30 seconds) **only as a controlled model**, unless a documented emergency exit is imposed by the risk governor. This research model is not broker parity and not profitable by default. No trailing-exit tuning to masquerade as improved entries.

**MANDATORY RISK/accounting:** BETA015_PROP_V1: $100,000 initial research capital, 0.01 fixed lot (100 oz/standard lot implies one-ounce exposure), one position total across specialists, $0.01/side historical fee assumption, 4% daily soft stop, 5% daily hard stop, $90,000 static overall floor, NY 17:00 risk day, broker/session validation, 0.25%-of-current-equity planned-risk veto, and all-in marked-equity accounting. Policy values may change only on a **new explicit owner request**, followed by a version bump, tests and fresh tick replay. Historical Coinexx fee is a scenario input until broker-current confirmation. Exact broker session/news calendar parity still pending. Do not claim an old script automatically invokes the BETA015 guard.

## 3. Offline teacher construction versus live causal features

1. First reconstruct the entry reference ledgers for R9 SYNTH, R9 REAL and R9 OVERFIT with provenance: feed, timestamp unit/timezone, bid/ask or generated-price conventions, buy/sell, entry-event timestamp, lot, and trade ID; distinguish **what the historical model did** from **what original Dukascopy actually permitted**. If precise event alignment is unverifiable, use **population-level structural comparison**, not a fake one-to-one oracle match.
2. On original Dukascopy raw ticks independently generate offline entry-opportunity labels at **pre-registered** forward horizons such as 3s, 5s, 15s, and 30s. Example executable markout at horizon `h`, for **0.01 lots / one oz**: LONG = `Bid(t+h) - Ask(t) - $0.02`; SHORT = `Bid(t) - Ask(t+h) - $0.02`. Use the first actual observed quote at or after the target time and record quote-gap/staleness. Markout is an **offline diagnostic**, not a causal decision feature.
3. Also track first-hit target versus adverse excursion, in true subsequent tick order, with predeclared thresholds and entry spread. Post-entry MFE/MAE and best-hindsight entry time are teacher labels only. Define eligible opportunity sampling/deduplication to prevent neighboring ticks in one market move being counted as hundreds of independent "correct" predictions.
4. Permit a strategy to look at only quote data and **completed higher-timeframe bars already available at that tick**. Confirmation time must include right-hand swing/fractal bars; late-confirmed pivots cannot be backdated. Train/freeze thresholds strictly before evaluating the next block.
5. Never train on, inspect, feature-engineer from, or tune against the sealed **August 2026** month. **January is discovery**; February–July were consulted in older BETA campaigns and are *reused in-sample / validation*, **not pristine untouched OOS**. After feature/parameter/model freeze, run genuine uninspected future data; August may be opened only after the owner explicitly authorizes the blind evaluation.

## 4. Entry scorecard — precision without deleting every trade

For each candidate, and for the unmodified identical-feed BETA reference, report both:

- **Directional precision / entry accuracy** on independent entry events (correct side under predeclared subsequent executable-path rule; denominator all triggered entries).
- **Recall / eligible-opportunity capture:** fraction of independently labeled tradable opportunities identified. Do not pass a filter that scores 100% on 2 trades while rejecting 99.9% of the opportunity universe.
- **Absolute correctly captured entry count, total entries, false positives, missed moves and signal duplication**, by month, session, volatility regime, spread bin and specialist.
- **Entry delay and displacement:** clock time and executable price paid versus the frozen causal setup; cost-aware 3s/5s/15s/30s directional markout, path-first favorable/adverse-hit outcomes, early MFE/MAE diagnostic and adverse-selection rates. Report actual Bid/Ask and $0.02 per completed position.
- **Same-clock / matched-event comparison** to the reference, not a favorable lifetime comparison when the reference account failed earlier. Maintain both a **SHADOW_DIAGNOSTIC** full-period series and a separately marked **FUNDED_FEASIBLE** chronology, never adding P&L or winning counts across them.
- **Mandatory safety constraints:** gross loss, after-cost P&L, daily/overall marked-equity DD, date of $90k termination, sample sizes, average spread, worst tail, and account integrity. An entry-precision rise with fatally worse economics does not qualify as a deployable advance.

Do not call a setup `R9 SYNTH matched` unless ledger matching against a *comparable execution population* is demonstrated. R9 SYNTH's historic impressive win rate is a teacher aspiration, **not** the denominator/accuracy benchmark for a different execution feed.

## 5. Market-structure hierarchy and specialist ablation

Candidate hierarchy (causal **roles**, not votes designed using future labels):

| Context horizon | Feature ownership |
| --- | --- |
| H4/H1 | Confirmed swing structure, current directional ownership, last confirmed BOS/CHoCH event |
| M45/M30/M15 | Prior completed range, channel/box geometry, breakout/sweep level, compression and structural invalidation |
| M7/M5 | ATR(14), directional efficiency, volatility expansion/contraction and state transitions |
| M1/S45/S30/S15 | Completed-bar acceptance/reclaim, failed-break timing, pullback stage |
| S5/S1/S250 | Fresh quote-side acceleration / ignition, gap & staleness checks |
| Ordered source TICK | Executable Bid/Ask fill, spread/cost veto, one-position router, marked-equity BETA015 risk gate |

Reconstructable independent entry families from BETA016/BETA017: (i) structure-aligned continuation + existing adaptive ignition, (ii) wick sweep then *later* completed reclaim and reversal, (iii) compression→expansion with body acceptance and optional later retest, (iv) controlled structural pullback→renewed ignition, (v) range-edge rotation, (vi) opening-range events where a broker/source-consistent session exists, and (vii) cost-toxic quote abstention (a filter, **not** counted as an entry signal).

Order: frozen reference → one family at a time → +one causal feature ablation → predeclared two-family combination → account-exclusive specialist router → regime-state hysteresis if justified. The router selects one of the eligible specialists or abstains, never adds independently simulated portfolio returns. Test structural confirmations, price action, tick momentum and volatility **separately first**, so any improvement can be attributed. For each variant, show absolute opportunity retention so "higher win rate" does not silently mean "hardly any entries." No black-box or non-reconstructible commercial indicators.

## 6. Promotion and handoff gates

- Entry-first **research milestone**: robust improvement in real-tick *precision plus meaningful recall / opportunity count* with acceptable funded survival and no material after-cost regression. No specific precision/recall numerical target has been adopted as a new owner criterion in this statement. A new owner request may define it.
- Keep HOLD and EXIT weighted lower/frozen. **Only when owner considers ENTRY sufficiently mature** and explicitly directs, change research priority to HOLD/EXIT persistence, harvest and favorable-path capture, using the then-current approved causal entry baseline.
- A positive **research diagnostic** is not a *formally promoted funded strategy*: the existing BETA003/006 human gate applies. Owner approval is required **before writing candidate MQL5**, then owner runs Coinexx XAUUSD M1 MT5 "Every tick based on real ticks", and decides on final acceptance. Until accepted, `approved_beta_ea=null` and `current_approved_baseline=null`.
- **Current evidence (BETA017):** every January variant was negative net; adding M5/H1 filters often eliminated absolute winning opportunities, so these remain research examples, not proof that market regime hierarchy solves entries. First scientific cache parity task still pending: `BETA_005_CACHE_INTEGRITY_CERTIFICATION__2026-01__002_FEATURE_PARITY_AND_CACHE_CERTIFICATION`. August remains SEALED.

**Source/governance relationship:** complements BETA004 campaign methods, BETA006 MT5 certification, BETA013/015 fixed research risk rules, and BETA016/017 testable structural-entry menu. This is a priority specification **without any newly executed strategy trial or asserted performance improvement**.
