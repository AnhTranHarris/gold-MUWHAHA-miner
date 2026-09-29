# BETA027 — raw-Dukascopy structural owner, entry accuracy, rearm and lifecycle salvage

**29 September 2026 · independent BETA research-only · August SEALED · NO promotion, no live MQL5 trading EA changes**

## Scope / scientific authority

Unfreeze HOLD/EXIT for *secondary* research while ENTRY remains the dominant objective. Reconstruct historically documented structural/acceptance/transition concepts from **original Jan–Jul Dukascopy tick Bid/Ask**, not retired R9B/Gamma code lineage or historical profit claims. R9 REAL is broker-historical comparator; SYNTH/OVERFIT offline teachers only, NEVER causal signal features or training labels.

BETA025/026 first-cycle R9-style study control: one first qualifying opportunity per UTC minute; completed second S1 efficiency≥0.60, bracket at start-minute midpoint±$0.15, ambiguous side chosen by observed midpoint, research source-spread cap $1.20, closed-M5 ATR/session. **This is NOT the full original Coinexx R9 EA**, which used a 25-point maximum spread and actual exit-dependent rearm. Never call this MT5 fill parity.

Recovered structural context: last fully confirmed M15 delayed-right-2 pivot high/low, H1 owner direction, previous completed M1 wick-vs-body acceptance and sweep, M5 ATR ratio, 250ms/1s/5s quote-change efficiency and quote-pressure proxy, historical toxicity states, reset/cooldown marker and separate actual one-position execution ledger. All M1/M5/M15/H1 bars were derived directly from ordered original ticks. Event tick index was regenerated using the BETA025 source emitter to disambiguate equal-millisecond quote ordinals (not by timestamp as-of search).

Jan–Jul: **57,527,562 original raw source quotes**, **191,674 first-cycle events**, **183,222 15s valid source-side markouts**. Fee $0.02/0.01lot=1oz model. Event accuracy includes actual source Bid/Ask spread, 15s last-quote markout. Seven months were **previously inspected**; they are NOT pristine OOS. M15 confirmed-pivot feature window and prior-month warmup are incomplete at monthly restarts. BETA005 17-layer parity pending.

## Seven-month ENTRY diagnostic, selected historical paired source teacher ±5s

| Causal source variant | Correct / valid +15s | +15s precision | Selected SYNTH teacher matches |
|---|---:|---:|---:|
| Existing BETA025/026 first-cycle source-style | **34,784 / 183,222** | **18.985%** | **34,394** |
| Weak 250ms opposing quote movement | 35,028 / 183,222 | 19.118% | 33,377 |
| Confirmed-level sweep structural FADE | 34,790 / 183,222 | 18.988% | 34,332 |
| Quote/path toxicity veto | 34,573 / 181,986 | 18.998% | 34,200 |
| Regime FADE + toxicity veto | 34,585 / 182,002 | 19.003% | 34,105 |
| Regime-aware weak-S1 owner | 34,764 / 182,002 | 19.101% | 33,416 |
| Structure-conditional 1s pending/confirmation | 34,132 / 179,397 | 19.026% | 33,736 |

The structural-only FADE affected merely 556/191674 events. No deterministic family convincingly raised **both** absolute after-cost correct count and source teacher alignment. All mean after-cost 15s markouts remained negative.

A separate depth-3 two-action LightGBM student trained **only** on Jan–Feb original Dukascopy executable +15s outcomes (36 causal features; no teacher labels) yielded an unfiltered bias threshold of 0.05 that raised correct count on common valid sample from 34,784 to **35,347**, but selected source-teacher matches on the same valid cohort fell **33,447→31,341**, and June/July regress. Another precision filter retained only 45,028/183,222 valid events and 13,313 correct; suppression not improvement. No learned model qualifies for promotion.

## Exclusive true-quote one-position execution (no funding)

Allowing a second R9-style candidate marker after observed midpoint recross, completed-S1 quality and 10s cooldown increased markers from 191,674 to **235,694**, but sequential portfolio excluded overlapping positions until actual observed exit.

| Fixed +15s tick exit | First-cycle | Qualified two-marker |
|---|---:|---:|
| One-position executed trades | 158,701 | 179,263 |
| Positive executed trades | 32,833 | 37,309 |
| Selected-pair SYNTH same-side ±5s | 30,433 | 34,025 |
| Shadow net 1oz USD | -114,001.73 | -128,005.01 |

**Decisive original unpaired teacher check:** For four COMPLETE original Coinexx logger days (Jan 02, Feb 20, May 20, July 20; **5,105 all SYNTH entries; 6,192 all REAL entries**), first-cycle executed side/time ±5s matches **883 SYNTH, 2,424 REAL**. Qualified two-marker executed comparison **873 SYNTH, 2,903 REAL**. Hence this rearm adds REAL-like churn rather than recovering SYNTH teacher events. Do not promote. The proposed R9 original exact position-after-exit rearm remains unreproduced.

## Lifecycle unfreeze: 24 Jan–Feb discovery parameters; 7 frozen follow-up variants Mar–Jul

All stop/target/trail/time decisions at observed next tick Bid/Ask, one position, fixed 0.01lot contract+fee. NO BETA015 prop-floor account: multi-month cash losses are **shadow-only, not capital-feasible funded returns**.

| Common source first-cycle entries, different exclusive hold | Trades | Winners | Win % | Gross loss | Shadow net |
|---|---:|---:|---:|---:|---:|
| Time-exit 15s | 158,701 | 32,833 | 20.69 | -144,745.53 | -114,001.73 |
| Time-exit 30s | 136,476 | 38,408 | 28.14 | -145,256.45 | -96,485.27 |
| Time-exit 45s | 113,219 | 36,581 | 32.31 | -136,286.06 | -79,309.66 |
| Time-exit 60s | 83,106 | 28,710 | 34.55 | -110,031.93 | -57,953.97 |
| 30s+$2 stop | 140,574 | 35,362 | 25.16 | -145,844.65 | -103,194.23 |
| 30s+$2 stop+$0.6 arm/$0.35 trail | 142,757 | 45,489 | 31.87 | -135,701.42 | -104,209.21 |
| 60s+$3 stop+$1 arm/$0.50 trail | 102,869 | 43,097 | 41.90 | -119,846.10 | -74,637.75 |

Higher success percentage can result from fewer trades or different exit shape, not genuinely better entry; even highest tested percentage remains loss-making. In particular 60s hold drops winners 32,833→28,710 vs 15s because exclusive account loses opportunities. Under 30s trail, per-trade net **worsens** roughly -$0.718→-$0.730 vs 15s despite much higher win %. No lifecycle qualified for promotion.

## Rebuild-ready MT5 logic (specification, not executable EA)

- A **persistent setup registry** with setup_id, frozen confirmed level, owner timeframe, activation time, age/touch and first/repeat penetration count, last reclaim, closing-bar acceptance, invalidation, trade/exit acknowledgement and expiry.
- **Market structure** H1/M15 confirmed completed levels (no unconfirmed pivot) -> **fast setup state** M5/M1/S5/tick separate body acceptance, wick sweep, failed break, compression, pullback -> route CONTINUE / FADE / PENDING with **genuine future observed tick confirmation only** -> spread/fees and BETA015 risk gate -> quote-side single position -> exact-tick hold/exit -> rearm ONLY after actual broker fill+close, observed recross and cooldown.
- Risk/fee/point/digits/contract/min-stop/tick-volume semantics must be broker-normalized. Source quote updates are not true signed deal flow. `OnTick` may coalesce incoming events; `CopyTicksRange` backfill and ordinal duplicate-millisecond handling should be bounded by CPU/queue constraints. The deployed MQL5 strategy needs explicit human approval, compilation and Coinexx real-tick tester/broker variation checks AFTER causal Python certification.
- Old P8/P9 economic claims, Gamma_2 retrospective timestamp ownership and historically profitable unverified models are **not** resurrected.

## Disposition and known gaps

**NO PROMOTION.** Retain BETA025/026 control and the mechanistic structural contexts; salvage level registry/acceptance/touch-age semantics as context only, not today’s profitable strategy. A full persistent 5s/M1/M5 pattern-event registry and its independent CONTINUE/FADE/PENDING transitions (as opposed to the tested row-mask approximation), original after-exit R9 rearm, continuous cross-month indicator warmup, entire original unpaired Jan-Jul teacher corpus, 17-layer BETA005 parity, capital-constrained BETA015 replay and cross-broker MT5 tester execution **remain to be certified**. August sealed. Entry stays higher priority than hold/exit.

**QA:** 78 bounded assertions passed (temporal pivot readiness, pending no-backdate, actual quote-side stop/gap, exclusive blocking, all 7 source months, original 4 complete sample-day teacher ledgers). QA does not certify scientific items explicitly listed as incomplete. Full local reproducibility archive in the BETA027 conversation: `BETA027_SALVAGE_AND_TICK_REPLAY_BUNDLE.zip`, SHA256 `2e728f13ddcb24934e860639b3455c6cac6ece18dff3babe0179c70e4e251221`; report `BETA027_SALVAGED_STRUCTURAL_OWNER_LIFECYCLE_RESEARCH_REPORT.md`, MQL5 translation `BETA027_MT5_STRUCTURE_EVENT_TRANSLATION_SPEC.md`. No Python scripts or binary blobs have been merged into a production EA.

Reference sources: [BETA026 predecessor](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/beta/research/BETA_026_COMPLEX_R9_ENTRY_ARCHETYPES_AND_FULL_TEACHER_SAMPLE_AUDIT.md), [historical source/error history](https://docs.google.com/document/d/1Ryzl9Ic2s1bkZgsWkKZ9btKfktqq4p4OmV80-UBh3z4/edit), [official CopyTicksRange](https://www.mql5.com/en/docs/series/copyticksrange), [OnTick](https://www.mql5.com/en/docs/event_handlers/ontick).
