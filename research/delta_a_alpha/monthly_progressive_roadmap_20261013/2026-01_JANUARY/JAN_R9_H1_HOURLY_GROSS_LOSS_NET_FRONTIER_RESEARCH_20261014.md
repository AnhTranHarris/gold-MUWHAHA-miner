> **SUPERSEDING OWNER INVESTOR-PERFORMANCE CORRECTION (2026-10-14): THIS IS NOT A SUCCESS OR ACCEPTED BREAKTHROUGH.** Any prior "breakthrough", "profit success", "large improvement" or "superior gross-loss control" wording below refers exclusively to relative **internal in-sample research**, not the owner's actual R9 SYNTH $100 target. R9 January net +$41,520.82/27,980 funded closes; the strongest prior Dukascopy experiment +$243.779/194 closes is **0.587% of R9 net and 0.693% of its trades**. Owner now requires >=60% of actual corresponding R9 hourly and daily performance before any human-facing success claim; <50% is failed internal research. See [binding correction and 1,536 further full-original-tick trials](OWNER_20261014_R9_60PCT_SUCCESS_GATE_RETRACTION_AND_1536_FULLTICK_TRIAL_ARCHIVE.md). Preserve all historical detail below without treating this document as approved or deployed. Git commit history retains original bytes.

# January 2026 — R9 H1 hourly gross-loss and net-profit frontier

**Date:** 2026-10-14. **Lineage:** `delta-A-alpha` experimental research. **Status:** January in-sample source-complete result; owner QC pending. No frozen V1 production change, J0183 unchanged, MT5 trading off, August sealed. This is subordinate to the [January original-source QC law](https://docs.google.com/document/d/15psoEliXaPEXJr22cKlJb4OGmWo26j3Eu8GlTtH26Kw/edit), full frozen owner V1 code, and the [10-page R9 institutional reverse-engineering report](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/delta-A-alpha/research/delta_a_alpha/monthly_progressive_roadmap_20261013/2026-01_JANUARY/R9_JAN2026_INSTITUTIONAL_QUANT_REVERSE_ENGINEERING_SOURCE_OF_TRUTH_10P.md).

## 1. Quant result — NET and gross loss move in the desired directions

| Jan original real Dukascopy $100, 0.01 lot assumed 1oz | Frozen positive ATR research control | **Preferred M1 phase × M5 ATR loss protection** | Highest net among nearby combined tests |
|---|---:|---:|---:|
| Booked net USD | **+$171.868** | **+$243.779** | +$247.706 |
| Gross profitable closes | +$815.524 | +$682.390 | +$704.160 |
| Gross losing closes | **−$643.656** | **−$438.611** | −$456.454 |
| PF | 1.267018 | **1.555798** | 1.542675 |
| Distinct physical funded closes | 244 | 194 | 192 |
| Win ratio | 60.66% | **64.95%** | 64.06% |
| Original tick-marked peak equity DD | $45.569 | $47.389 | $50.839 |
| Active UTC hours; positive/negative | 158; 92/66 | **134; 84/50** | 135; 84/51 |
| Positive / negative UTC funded dates | 15/6 | 13/6 | 13/6 |
| Jan 1–15 net | +$2.230 | **+$20.709** | +$22.399 |
| Jan 16–31 net | +$169.638 | **+$223.070** | +$225.307 |

Preferred improvement vs same physical source control: **+$71.911 (+41.84%) net**, **$205.045 (31.85%) less absolute booked gross loss**, 50 fewer funded closes (−20.49%), and $1.82 *larger* peak intratrade equity DD. These are January-only fitted hypotheses, not prospective or broker-validated performance. $200 initial-capital independent replay earned the same dollar result; ending close balances were **$343.779 / $443.779** for $100 / $200.

## 2. H1 hourly investor target and like-for-like accounting

The R9 Coinexx **"Every tick" generated-tick M1/M5/H1 workbooks are the same 27,980 trade cycles**—never triple count. Reported January net **+$41,520.82**, gross losses **−$1,827.87**, **480 close-active hours**, ~**$86.5017 net/hour**, **58.2917 closes/hour**, and **$3.8081 gross losses/active hour**. Worst within single H1 report bar gross losing closes ~−$9.18. Original R9 peak **closed-balance** DD $3.40 is NOT floating risk.

New preferred Dukascopy student: **$1.81925 net per active hour**, **1.448 closes per active hour**, **$3.27322 gross loss per active hour**, worst UTC clock-hour gross losses **−$23.177**, 134 active hours / 610 zero-close hours (all 744 exported). Its *mean* funded-active-hour booked gross loss is below R9's *synthetic* $3.8081, but its worst hour is materially worse and its hourly profit and velocity remain roughly **47.5× and 40.3× below** R9, respectively. Source clock offset for exact hour-by-hour R9 comparison is inferred ~UTC+2, not independently certified. Do NOT treat gross-loss total alone as comparable when volumes differ so drastically.

## 3. Precisely reconstructible causal mechanism

**Parent source:** exactly 627 unchanged, original January **completed-S15 BB/Keltner squeeze-release** virtual signals. **L0/L7:** ordered immutable original Dukascopy UTC Bid/Ask at every tick; one physical position, minimum 250ms latency from signal, 15-second max pending queue, spread ≤$0.55, quote-side drift ≤$1.50, round-trip commission modeled $0.20 cash, assumed leverage 1:500, initial $100/$200, physical 0.01 lot assumed 1oz. New-entry shutdown when modeled account equity falls below 60% initial; no lot doubling or averaging losses.

**Entry-risk shield:** At the original *as-of* second when an independent S15 source emits a new signal, require `((signal_utc_ms // 1000) % 60) >= 2`, excluding source proposals at minute second **00**. The candidate uses only the present timestamp and signal; no R9 future win/entry labels or unfinished current M1 candle. Thresholds 2 through 15 yielded the **same funded January trades because this source emits on S15 boundaries**. Do not generalize that equivalence to arbitrary other indicator streams.

**M5 ATR continuation:** Use only last *completed* M5 ATR(14), computed on original Dukascopy Bid series. At ATR ≥$7.77: $7 source stop, $40 gross target, $7 favorable trail-arm, $3.50 trailing gap, **1,500s** max hold. Otherwise: $7 stop, $20 gross target, $5 trail-arm, $2.50 gap, 1,500s max hold. The original positive research parent differs by having 2,700s hold in high-ATR environments. A source-authentic MQL5 `iATR` parity test is still required before porting any numeric threshold.

**2×2 factorial test with high-mode hold frozen at 1,500s:**

| M1 minute-open shield | M5 ATR runner | Net | Trades | Gross loss | PF |
|---|---|---:|---:|---:|---:|
| Off | Off | +$110.096 | 250 | −$641.703 | 1.17157 |
| Off | On | +$164.238 | 245 | −$639.793 | 1.25671 |
| On | Off | +$181.417 | 199 | −$440.458 | 1.41188 |
| **On** | **On** | **+$243.779** | **194** | **−$438.611** | **1.55580** |

The M1 shield alone added $71.321; M5 ATR lifecycle alone added $54.142, with a **+$8.220 net interaction** in this same-month comparison. Interaction is an accounting difference-in-differences, not a significance or causation proof.

**Funded occupancy attribution vs prior $171.868 child:** 185 matched source signal timestamps, matched source net change **+$0.100**; 59 displaced parent-only funded trades had net **−$58.433**, while nine newly executable source opportunities earned **+$13.378**. These sum to **+$71.911** correctly; the current policy reruns real unique positions rather than simply deleting historical losing trades from a report.

## 4. Independent complete tick audit and custody

Independent QA reread and SHA-verified **9,135,062 original January quotes** from `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz` (SHA256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`). Verified every funded signal belongs to the exact original **627 signal-event source**, original entry and exit Bid/Ask quote prices, model latency / spread / drift, $0.20 booked fee, one strict physical position, fully marked opposing-side tick equity while each position open, 100/200 account reconciliation, zero open month-end inventory. **194/194 entries + 194/194 exits independently matched; zero audit exceptions.** 31 UTC dates, all 744 hourly rows, ISO-week ledgers and full ticket-level ledger saved for each capital size.

Preferred verified: gross wins +$682.390; gross losses −$438.611; 194 closes (126 winners, 68 losses), +$243.779 booked; 13 positive / 6 negative dates; 84 positive / 50 negative close-active hours; full tick-marked DD $47.389; zero new-entry equity halt. Original R9 H1 native tester report still a **generated-tick comparison**, not the same feed, and its gross-loss/DD definitions cannot be silently equated with the student's tick-marked equity.

**Research negative/alternative record preserved**, not promoted: 74 source stop/aged-loss configurations; 84 trailing guard alternatives; 51 entry-phase/session alternatives; 60 combined ATR hold settings; 4 factorial control states = **273 January configuration trials**, some economically equivalent under S15 timestamps. These runs were fitted to January and **must not be presented as independent unseen-month confirmations**. All original codes/results/source hashes are inside the immutable companion research bundle; original large Dukascopy file is linked by SHA but not unnecessarily duplicated.

## 5. Reconstructible public strategy mechanisms (inspiration only)

- [MetaQuotes finite cycle grid regime BGT/TGT/MGT](https://www.mql5.com/en/articles/21833): explicit state transitions and bounded cycle exits, **not** open-ended basket/martingale.
- [MetaQuotes published BGC grid source](https://www.mql5.com/en/code/70764): CUSUM/volatility-break regime differentiation; **future candidate**, not imported profitable code.
- [Chinese/English FMZ ATR trailing implementation](https://www.fmz.com/strategy/432794), [FMZ dynamic stop logic](https://www.fmz.com/lang/en/strategy/430748): causal one-way trailing stop state adapted conceptually to tick-executable original quotes; not XAUUSD verified profits.
- [TradingView open-source HTF liquidity sweep/reclaim](https://www.tradingview.com/script/FG507Q8S-HTF-Liquidity-Sweep-Reclaim/) and [confirmed sweep–reclaim–retest](https://www.tradingview.com/script/pqn79edL-Sweep-Reclaim-Retest-Clean-v1/): finite pending signal states and invalidation; **not yet a tested funded addition**.
- [TradingView CHOP+DMI/PSAR exits](https://www.tradingview.com/script/GrP0zABg-CHOP-Zone-Entry-Strategy-DMI-PSAR-Exit/): potential regime-specific fast replenishment; also **unfunded/untested** here.
- [MQL5 mathematical risk of unbounded grids](https://www.mql5.com/en/articles/8390): rationale for finite physical exposure and account heat control.

## 6. Code delivery, frozen V1 boundary and next gross-loss improvement

New Python **experimental child**, not live connected: `jan_r9_teacher_m1_phase_risk_v1.py` (full tick executor), `jan_phase_plus_atr_harvest_neighborhood_v1.py`, `jan_gross_loss_stop_age_frontier_v1.py`, `jan_profit_protection_trailing_grid_v1.py`, `jan_r9_m1_phase_independent_quote_qc_v1.py`, `jan_phase_atr_factorial_ablation_v1.py`, and separate opt-in `jan_r9_m1_phase_atr_loss_governor_v1.py` with 5 passing unit tests. All are source-readable Python modules, no native EA alterations. Dependencies `r9_teacher_informed_dukas_executor.py`, original parent `jan_parent_causal_squeeze_signals.npz`, and previous source generator preserved in same ZIP. Frozen protected V1 core remains unchanged; owner source-lineage and complete QC needed before acceptance.

**High-value next step:** preserve this gross-loss shield *for its own S15 source only*, and develop a separate **event-clock quote-burst / H1-M5 structure / session-aware fast virtual-grid rearm specialist** with an *independent positive after-cost opportunity*. It must raise **funded net/hour** and **active-hour participation** under one shared L7 slot without worsening gross-loss/hour and worst-hour. Do not add fast losing transactions merely to approach 27,980 synthetic fills. Do not silently import R9 hindsight prices, multiply lots, disable the $100 stop, or calendar-fit January dates.

**Promotion boundary:** Owner QC=PENDING; J0183 unchanged; no MQL5 order path enabled, no January-only date rule embedded in runtime.
