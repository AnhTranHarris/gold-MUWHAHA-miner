# F401-R44/R45 — Actual four-month causal model escalation scientific record
**2026-10-27 — EXISTING Gold MUWHAHAHA Miner / XAUUSD FILTER08, objective M-DK-01 — UNAPPROVED RESEARCH ONLY**

## Continuity / controlling methodology
Original governor v1.4 and signed 1.5-A1/A2/A3, whole-EA v1.1, source authorization, owner anti-amnesia, original 2,042-line FILTER08 forensic and 39-objective checklist. The original 8 broker-month R00 event indexes, sides, source quotes, and future 30–32s class labels are fixed. Fitted original R24 (814,995 wrong/9,999 correct lost across both broker populations) is a teacher/upper-bound **not** causal month-blind capacity. Best prior four-month *month-blind source-only conditional pending* R40: CX 54,852 bad / 2,215 right and DK 53,935 bad / 2,171 right. R40 +15s can affect only a never-submitted, still-UNFILLED signal intent; never retroactive order cancellation.

**Owner objective:** for each independent four-month broker population exceed 400,000 original incorrect signal vetoes with fewer than 10,000 originally correct vetoes and >50:1 wrong:good, while remaining exact past-only and forward-demo-feasible. This is a research objective, not a claimed verified achievable rate. Four original 2026 months were previously exposed; no truly virgin out-of-sample month is claimed. For Jan, first60% fit / next20% CAL / last20% evaluation; Feb/June/July previous-month CAL, previous source-only chronology, scored whole target month, no target-month cutoff optimization.

## New original market evidence (reused intact tick engine)
R44 introduced NEW 64-dimensional market features computed directly from registered eight original Coinexx/Dukascopy raw tick streams, not from R24 hindsight scores: (1) **three event-time directional-change state machines** keyed to $0.10/$0.25/$0.60 reversals, with signed regime/pivot age/overshoot/reversal count; (2) **completed and published M1/M5/M15/H1 bars**, side-relative bodies and prior bar deltas, close locations, range/quote-age, no partial candle. All source quotes are consumed only while `quote.timestamp < original_event.t0`; equal-ms future ordinal observations are omitted. Sixteen earlier-month raw source pins unchanged, eight active months verified; SHA256 per derived source in `cells/R44_FULL_EIGHT_SOURCE_MANIFEST.json`. Existing R37 source-native raw ticker and R39 previously-matured features imported, not rebuilt.

## R44 high-capacity boosted candidate — bounded hard fast-fail
R44 model uses 185 original as-of inputs (121 inherited original R37/R39 plus new 64 causal). Three head families: 3-class correct/opposite/neutral, 2-class bad hazard, and independent directional-change microstructure hazard. Six protected-correct/nonlinear consensus score combinations. Per-source month CAL-only <=0.6% correct-loss budget and frozen thresholds; original January last20 source and STRICT opposite broker excluded scored AFTER freeze. The original January result:

| Source trained and frozen | Same-source Jan final20 wrong/right veto | Opposite-broker EXCLUDED Jan final20 wrong/right veto |
|---|---:|---:|
| Coinexx | 6 / 7 | Dukascopy: 21 / 23 |
| Dukascopy | 17 / 11 | Coinexx: 43 / 58 |

This fails even basic selectivity and is substantially weaker than the archived R39/R40 historical controls. Under governor 1.5-A2, **R44 same-family February/June/July fits deliberately NOT RUN**: no futile tree/grid escalation and no false full-four-month R44 claims. All raw derived market features preserved for distinct successors. January models, freeze hashes, original event masks in `run/` are retained. Result state **REQUIRES_REPAIR/RETIRED_CONFIG**.

## R45 HARD architectural escalation — online prequential four-context state
R45 is **not** an incremental R44 tree or threshold tweak. It abandons static label-fitted gradient boosters and uses four separate source-native hierarchical conditional error-hazard memories. At every original event t0, current state is estimated from past native directional-change, completed HTF, original bid/ask quote update and UTC regime contexts; the **only** label update permitted is from an earlier original event whose full future observation has matured at `t_prev + 33001ms <= t0`. Runtime class labels of the CURRENT signal never update its prediction. Streaming state is updated only forward in time and can be replayed without future labels. January first60 model adaptation, middle20 cutoff calibration, final20 scored; Feb/June/July model context adapts chronologically from fully matured earlier events only; source broker streams completely isolated. Per-month thresholds freeze BEFORE scored month using only previous source month outcomes. Five regimes/consensus scorers, <=0.6% CAL right-veto budget; all original source validation arrays and masks are frozen.

| Broker | Scored source month | Originally incorrect veto | Originally correct veto | Wrong:correct |
|---|---|---:|---:|---:|
| Coinexx | January last20% | 14 | 23 | 0.61:1 |
| Coinexx | February full | 6,236 | 4,830 | 1.29:1 |
| Coinexx | June full | 3,509 | 2,526 | 1.39:1 |
| Coinexx | July full | 9,922 | 6,700 | 1.48:1 |
| Dukascopy | January last20% | 13 | 16 | 0.81:1 |
| Dukascopy | February full | 27,507 | 17,296 | 1.59:1 |
| Dukascopy | June full | 1,653 | 907 | 1.82:1 |
| Dukascopy | July full | 3,489 | 1,749 | 1.99:1 |
| **Coinexx combined scored JAN-TAIL+FEB/JUN/JUL** | **not complete January** | **19,681** | **14,079** | **1.40:1** |
| **Dukascopy combined scored JAN-TAIL+FEB/JUN/JUL** | **not complete January** | **32,662** | **19,968** | **1.64:1** |

**No improvement over R40.** Both R45 broker-calibration budgets failed to transfer to the independently scored months, and gross incorrect rejection is far short of 400k with excessive right veto. This is a constructive negative; save source, freeze configs, 8 masks, class splits. Full eight train/CAL/score cycles completed independently per broker; this R45 test is *broker-separated prequential*, not source-broker weights fitted then transferred frozen to opposite broker. Do not call its two environments rigorously broker-excluded model transfer; the stricter R44 January DID score excluded-broker frozen heads. R45 can use each broker's own **already matured past** outcomes to adapt, exactly what an instrumented future demo could observe, but would need a live event/label source.

### Causal audit
- Four deterministic targeted Python tests passing: exact quote t0 boundary, completed-bar publication, future label poisoning cannot alter earlier decisions, causal memory response to matured labels.
- Frozen month policy BEFORE reading/scoring target-month results; `run/R45_{broker}_{month}_FREEZE_BEFORE_SCORING.json` each with source-scoped CAL cutoff.
- Original event t,side,truth and valid array alignment checked against R37 original source manifest before training. For R45 output, all 8 masks and freeze digests recorded; no t0 backdating, no future teacher probabilities, no original label used at inference.
- Missing full 4,178 R9 correctly-directed emitted supply quota replay, MQL5 compilation/MT5 realtime integration, quote-server availability and shared-capital after-cost fills mean **no demo active filtering** and **no economic/tradable return claim**.

## Community-mechanism scout (ideas only, NOT external training data)
1. Tsang et al (2024), FX directional-change nowcasting, DOI 10.1002/isaf.1552. R44 adapts past observed directional-change state; no external prices or imported code. Negative R44 exposes insufficient separation under this stage's event contract.
2. Bao et al (2025), *Calibration after Adaptive Pick* in JMLR 26/287, https://www.jmlr.org/beta/papers/v26/24-0452.html. Investigate strictly historical conditional coverage for selective error veto; its exchangeability/selection assumptions are not automatically valid for correlated XAUUSD five-second events, thus **no guaranteed error control**.
3. River progressive validation reference https://github.com/online-ml/river/blob/main/river/evaluate/progressive_validation.py demonstrates delayed-label online evaluation; R45 independently implements a simple strictly matured event-clock update, not third-party code import.
4. MetaQuotes CopyTicks https://www.mql5.com/en/docs/series/copyticks and runtime queue https://www.mql5.com/en/docs/runtime/running: OnTick notification is not every quote, so live features must capture original ordered bid/ask `MqlTick.flags` and prevent duplicated/nonmonotonic tick ordinals. Strict future-bar/tick data must be rejected.

## Next genuinely different scientific mechanism — R46 NOT RUN
Source-native **contrastive predictive state encoder** of as-of-t0 ordered bid/ask quote-update sequences, self-supervised on strictly prior-month quotes, *without* target outcome labels. Add causal asymmetry of bid-only/ask-only/joint-update runs and quote-time entropy; model separate opposite and neutral competing hazards conditional on completed HTF phase, and an independently trained correct-rescue guardian. Freeze broker-excluded student and matching proper-score calibration before target-month replay. Test controlled same-hour/side placebo and R40 matched event subset, require genuine new informational lift, and abort when it is again below preserved R40. For any delayed 2/5/10/15s confirmation, quantify selection/fill loss separately and **only** veto a real order intent which has never been sent. Execution opportunity changes and t0 market orders are distinct experiments. No automatic re-entry using current-event future outcome. Event-level 8-cell and stage-per-cell G06 are distinct from function-level M-DK-01 comparison.

**Owner approval:** unchanged 21/39 historically accepted. **Active checklist:** M-DK-01 OPEN. **G01-G09:** all OPEN. **No new live/demo filter permission**, no MetaEditor MQL5 compilation or Python↔MQL5 bitwise parity demonstrated. PRIMARY READ-ONLY, unapproved MT5_EXPAND/01 only, never /02. No backtest engine rebuild or fake positive evidence. R40 remains currently strongest completed month-blind research control for still-unfilled conditional pending orders.


### Exact archived original executable source and masks
MT5_EXPAND /01 uploaded archive: https://drive.google.com/file/d/1evb7X35ZQcsJNREgO9VKnuBMlE_YFL9J/view
Archive SHA256: 193df2657ec5dfa310e75ec4c19f18fe846b23e8b89e75f749ec74ca49d192ef; 46 ZIP members, ZIP CRC PASS, embedded SHA manifest. Full original eight source derivative SHA entries recorded `cells/R44_FULL_EIGHT_SOURCE_MANIFEST.json` inside archive, 8 scored R45 masks and all R44 models. This branch currently provides scientific receipt; Python executable source is in unapproved original archive, not separately committed as tracked tree files. No production EA or prior baseline altered.
