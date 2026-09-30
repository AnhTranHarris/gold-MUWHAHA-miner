# BETA041 — Five parallel adaptive families including pre-entry BUY/SELL lead-up

**2026-09-29 | Independent `beta` source research | NO PROMOTION | August SEALED**

## Investment-relevant decision

**Fifteen configurations tested (five families, three bounded settings each); ZERO pass the full strict >10% gate and original-winner preservation gate. No strategy has positive realized net. No January–July expansion is merited.** The fifth, owner-requested family was not another confirmation veto: it learned from **31 observed quote-path variables strictly BEFORE the R9-like E060 opportunity event** to propose KEEP BUY/SELL vs REVERSE BUY/SELL and choose a stop/hold/target profile. It produced only **+$11.06** of modeled net improvement on Jan11–18 (**0.245% relative reduction of negative net**) with ten direction reversals, four additional positive closes and three fewer preselected SYNTH side/time matches. It is **not proven predictive**: incremental directional AUC ≈0.498, statistically indistinguishable from chance in this inspected period.

Source: Jan1 00:00 UTC through Jan18 12:00 UTC exclusive, **4,205,709 original ordered Dukascopy XAUUSD Bid/Ask ticks**; parent E060 R9-like **14,174** first-cycle opportunity events. Time-based training Jan1–Jan9 (6,466 labeled events), embargo Jan9–Jan11, diagnostic Jan11–Jan18 (6,473 origins). This later period was repeatedly viewed in prior research; it is NOT fresh blind OOS. All permitted entries preserve E060 source event provenance, no extra mandatory MTF/structure/oscillator admission filter, actual 0.01-lot assumed 1 oz BUY Ask / SELL Bid, first real opposite-side close observed, $0.02 assumed roundtrip and **one** chronological active position. E060 itself remains a source-eligibility generator with prior S1 and relaxed $1.20 quote-spread controls; “no confirmation filter” never means ignore broker order validity or risk.

### Matched Jan11–18 evaluated one-position outcomes

| Variant with best tested setting per family | Net USD | Improvement vs -$4,516.45 | Closed / profitable | Baseline SAME-EVENT winning trades preserved | Selected historical SYNTH ±5s same-side matches |
|---|---:|---:|---:|---:|---:|
| Original E060 L30/SL2/TP2 baseline | **-$4,516.45** | — | 6,114 / 1,196 | 100% | 1,114 |
| Regime-selected scalp/runner durations | **-$4,133.14** | 8.487% less negative | 5,573 / 1,206 | **72.993% — FAIL** | 1,114 |
| Live in-position runner re-evaluation | **-$4,445.64** | 1.568% less negative | 6,002 / 1,247 | 92.642% | 1,114 |
| **Fifth: pre-entry lead-up BUY/SELL** | **-$4,505.39** | **0.245% less negative** | 6,114 / 1,200 | **99.916%** | **1,111** |
| State-specific predicted exit choice | **-$4,515.36** | 0.024% less negative | 6,114 / 1,196 | 100% | 1,114 |
| Global predicted exit choice | **-$4,516.45** | 0% | 6,114 / 1,196 | 100% | 1,114 |

All 15 configurations had negative net. The strongest regime duration family changes post-entry time opportunity sets; its gain of ~$383.31 cannot be presented as standalone profitable direction or as additive to any other separate strategy's P&L. Over the **entire 17.5-day discovery window**, the same pre-entry fifth setting moved the baseline net **-$10,375.74 -> -$10,347.26** (+$28.48, 0.274%) while changing the source action at a tiny subset of events. The regime duration family full-window net was -$9,380.80 (9.589% reduction) but only 72.236% of baseline same-event winners were preserved; it did not pass the combined condition. **No candidate progressed to Jan–Jul**.

### Fifth family state construction: what happens BEFORE an entry

For each source R9-like opportunity `(origin_time_ms, original_tick_ordinal, original_side)`, take as **pre-entry anchor** the final quote whose `time_msc < origin_time_ms` (exclude ALL quotes with equal origin timestamp). At anchor `t−`, for horizons `h ∈ {250 ms, 1 s, 5 s, 15 s, 30 s, 60 s}` reconstruct from previously seen quotes:

1. Change in bid/ask **mid** price (`mid(t−) − mid(t−−h)` USD/oz).
2. Move normalized by observed historical price scale.
3. Historical **quote arrival rate** (`number of source quotes / h`; **NOT** real traded volume, buy/sell aggressor activity or DOM order flow).
4. Historical relative change in spread (`spread(t−) − spread(t−−h)`).
5. Seven further deterministic acceleration, multi-horizon compression, arrival-rate-ratio and spread-acceleration descriptors.

These **31 strict pre-event inputs** complement 60 as-of-event source-state features (microstructure and confirmed M1/M5 level memory and completed H1 ownership) plus 16 original-side-signed transforms of prior quote measurements, for **107** input columns total. The fifth fitted Ridge model (alpha 650; train-only standardization/clips, six fully costed buy/sell×scalp/control/runner training outcome labels) predicts `U(KEEP,L30)` and `U(INVERSE,L30)` and reverses direction only when the predicted advantage exceeds **$0.8, $1.4, or $2.2** in the three *predeclared* settings. An exit-profile change additionally requires predicted payoff improvement >$0.60 over original L30. Actual entry is STILL the first original E060 observed quote: **this lead-up classifier did not implement an independent anticipatory entry clock**. The predicted action does not read future prices; training-only targets come from future quote execution. Portability requires the entire manifest feature order and 6×107 matrix; no black-box model is accepted.

The leading setting changed **10/6,473** diagnostic original-side decisions; selection can be luck. The self-standing incremental information test fitted three separate models on training-only future labels for `INVERSE-L30 payoff minus KEEP-L30 payoff`, then checked their diagnostic AUC (chance 0.50): original 60 features **0.49304**, 31 strict lead-up features alone **0.49753**, full 107 **0.49778**. None demonstrates directional discrimination. Do not report the extra predictors as a realized alpha breakthrough.

### Other four distinct families

- **Global predictive exit revaluation:** Original trade direction, L30 unless global 6-action predictor's expected KEEP exit benefit is above a fixed $0.3/0.6/1.2 threshold. Actual observed-time scalp or runner trade management if selected. No entry veto.
- **Four-regime conditional exit revaluation:** Same independent mechanism with a global+specialist blended predictor. No entry veto.
- **Regime-adaptive duration:** Confirmed current source states select one of short/medium/long profiles at entry, without suppressing the event. Can lower gross loss by making position unavailable longer; must preserve same-event winners and future opportunity capacity.
- **Live runner re-evaluation:** During open actual tick stream, after age≥8s and observed MFE exceeds 0.50/0.85/1.20 with current favorable path persistence, extend hold up to 60s; actual stop/trailing/target/hard time expiry. No optimum stop at hindsight MFE and no simulated future quotes.

### Why the result is NOT an investor strategy

- The best percentage-loss-reduction family erased over one-quarter of baseline winning **event identities** even though its total positive close count increased. This violates the user-mandated retention guard.
- The fifth family had only 10 action changes and no directional AUC advantage. It is an implementable prototype, not proof of improved entry recognition or ability to predict direction.
- Full one-account modeled baseline floating drawdown Jan1–18 was about **$10,375.84**, but this research lacks the BETA015 actual $100k→$90k equity floor, NY17/day $4k/$5k lockouts, executed margin and broker restrictions. These results therefore are **NOT capital-feasible simulated funded account returns**. Actual Coinexx spread/contract/slippage not verified.
- Selected R9 SYNTH teacher alignment uses **prepaired** original REAL/SYNTH pairs, not all unselected 17.5-day original R9 logs. The teacher is an evaluation reference and never used to train. The true latent Gold Hunter V8 entry/exit rules are unresolved.
- BETA005 17-layer materialized data/feature parity unfinished. August SEALED. All Jan–Jul already inspected, hence no pristine OOS claim.

## Reproducibility and decisive next family improvement

Original source compressed byte SHA256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`. Main `BETA041_FIVE_FAMILY_PREENTRY_LEADUP_RESEARCH.py`, complete 15-case results JSON, `BETA041_PREENTRY_LEADUP_MT5_NUMERIC_MANIFEST.json`, `BETA041_PREENTRY_INCREMENTAL_INFORMATION_AUDIT.py`, independent `BETA041_INDEPENDENT_CAUSAL_AND_ECONOMIC_QA.py` (166 tests PASS) and source-hash ZIP manifest stored in BETA041 reproducibility bundle. All raw monthly market gzip files external; ONLY original January file actually opened this BETA041 unit. Rerun commands:

```bash
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=4 python BETA041_FIVE_FAMILY_PREENTRY_LEADUP_RESEARCH.py
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=4 python BETA041_INDEPENDENT_CAUSAL_AND_ECONOMIC_QA.py
OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=4 python BETA041_PREENTRY_INCREMENTAL_INFORMATION_AUDIT.py
```

Code depends on archived BETA022/23/25/26/27/28/29/33/40 research helpers, included in bundle, and the original quote month at `/mnt/data/XAUUSD_DUKAS_2026_01_ticks.csv(3).gz` and preexisting hash-grounded BETA040 source event fixture. `numpy`, `pandas`, `numba`, `scikit-learn` required.

**NEXT STRUCTURALLY DISTINCT TEST**: The fifth family should acquire an independent PRE-E060 *action-clock hazard* for LONG/SHORT/WAIT over original M1 bracket/confirmed prior levels, using only observed quote arrivals, cost-normalized expected sign and compress→expansion state age. Compare the **first actually observable entry quote after hazard** against baseline entries, with a fair full original-side event and teacher ledger. Apply competing-risks post-entry hazard to HOLD/EXIT, with fully reconstructed per-tick state and one-position opportunity cost. The public open-code literature below suggests reconstructible choices but NONE establishes a profitable XAUUSD tick edge:
- [MQL5 BOCPD state break](https://www.mql5.com/en/articles/23482)
- [MQL5 HSMM duration-aware regime](https://www.mql5.com/en/articles/24460)
- [MQL5 competing-risks exits, including negative examples](https://www.mql5.com/en/articles/24106)
- [TradingView open pre-breakout volume/compression source](https://www.tradingview.com/script/1VI2ivGw-Pre-Breakout-Scanner-Volume-Compression/) — **real volume NOT present on Dukascopy quote data; use quote intensity instead and do not mislabel it**.
- [MQL5 XAUUSD RL + purged validation and null live evidence](https://www.mql5.com/en/articles/21314)
- Public GitHub [TrendFlowing EA](https://github.com/Piardian/TrendFlowing-Forex-EA) GPL-3.0 and [Breakout EA](https://github.com/quantwrench/mt5-breakout-ea) MIT: code architecture reference ONLY, no copied closed-source or claimed gold edge.

No new official MQL5 EA code without explicit owner approval; owner later supplies *only* compact Coinexx MT5 M1 Every tick based on real ticks report after approved build.