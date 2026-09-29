# BETA032 — 17.5-day January fast-screen and seven-month frozen recheck

**2026-09-29** · BETA branch only · `NO PROMOTION` · 2026-08 **SEALED**.

## Investors' result

**123 source-reconstructible original-quote entry variants** screened January 1 00:00 UTC–January 18 12:00 UTC (**17.5 calendar days**). **7** exceeded a *preliminary* 10% reduction in costed 15s markout loss with the predefined eligibility/gross-loss/origin-win safeguards. **6** frozen nearby settings were immediately retested on all **57,527,562** original Dukascopy Jan–Jul XAUUSD bid/ask ticks, with **no retuning**. **NONE** sustained >10% full-period loss reduction, **NONE** reached desired >20%, **ALL** remained after-cost negative. No EA approved.

| Same-feed identical executable evaluation | Parent BETA025/026 E060 | Screened prospective rule | Verdict |
|---|---:|---:|---|
| January 17.5-day origin+15s after-cost markout | **-$10,483.13**, 14,174 eligible / 13,566 evaluable / 1,714 positive | After exactly 1s, FIRST observed fresh quote, flip unless original-side midpoint displacement >=$0.15: **-$9,288.69**, +11.394% loss reduction, +4.784% correct, 96.7% emitted events retained | January preliminary screen ONLY |
| Jan–Jul same rule, frozen | **-$132,571.24**, 191,674 eligible / 183,222 valid / 34,784 positive | **-$130,815.13**, +1.325% loss reduction, **-6.592%** correct entries, **-52.262%** selected SYNTH matches | REJECT |
| Jan–Jul best absolute markout improvement in six frozen rules | -$132,571.24 | Quote-sign pressure evaluated after 1s, side reversal when signed 1s quote-pressure < +0.20: **-$129,467.87**, +2.341% loss reduction, -5.390% correct, -50.11% selected SYNTH matches | REJECT |
| Jan–Jul parent/1s-$0.15 L15 **one-position shadow** | -$114,001.73 / 32,833 wins | -$114,512.55 / 31,927 wins | ECONOMICS WORSE; no funded BETA015 |

**No full-seven-month result with >10% gains; no trade entry/hold/exit strategy qualifies for owner-approved MQL5 code.** The short-window advantage was localized to January; Feb/Mar/Jun/Jul often regressed in absolute source markouts. Relative net-loss reductions cannot be described as positive trading profit, or cross-broker percentage uplift.

## REAL/SYNTH actual ticklogger reality check

Only the complete unselected source logger on **Jan 2, 2026** was locally available inside the initial 17.5-day window. It contains **1,525 original REAL**, **1,083 original SYNTH** trade entry markers. For the matched Dukascopy original event clock at ±5s:
- Parent: **736 REAL** same-side matches, **215 SYNTH** same-side matches.
- 1s wait/$0.15 reversal: **135 REAL**, **100 SYNTH** same-side matches.
- A large match reduction is not a reconstruction of SYNTH profitability.

All other Jan initial-window source-teacher comparisons use the original **preselected** R9 REAL↔SYNTH same-minute/side/ordinal pair ledger, **10,165** selected records in the window; full original 17.5-day teacher recall is NOT CLAIMED. Jan–Jul selected-cohort SYNTH parent 34,394; all six delayed action routers lose 44%–58% of those matches. Full Jan–Jul sample teacher matching is **biased** by the original pair selection and does not substitute for complete raw logger alignment.

## Observed-event formula, reproducible in a future authorized MQL5 EA

R9-like causal one-origin-first-cycle emitter supplies `(t0, side, original_tick_ordinal)`. Branches do **NOT** enter at t0 if delayed:

```
qt = first observed Bid/Ask quote with time_msc >= t0 + delay_ms
if qt absent or quote_age>2000ms: CANCEL, no retroactive fill
directional_move = original_side*(mid(qt)-mid(t0))
KIND2: side = original_side if directional_move >= threshold else -original_side
KIND6: Q=(num_up_midquote_changes - num_down_midquote_changes)/
          max(1,num_up_midquote_changes + num_down_midquote_changes) in last 1s at qt
       side = -original_side if (Q*original_side) < threshold else original_side
BUY executes at qt.Ask; SELL at qt.Bid. Reverse-side closing at first recorded
quote on/after original t0+15s (<2s quote staleness), 0.01 lot=1oz,
modeled fixed $0.02 roundtrip fee. Independent one-position L15/L30/L45
lifecycle on every original later quote, no concurrent positions.
```

This is a **Dukascopy non-broker-parity** reference; older BETA025 $1.20 spread research gate differs from Coinexx original R9 ~$0.25. First origination and ordered quotes preserve event-id and same-timestamp source order. No future teacher label or original t0+15s outcomes enter rules; those are OFFLINE scores. Jan–Jul previously consulted; none is pristine OOS. Historical original R9 OVERFIT/Gamma profit claims and Gold Hunter V8 opaque internals NEVER imported.

## Scientific durability and QA

Local **BETA032_FAST_SCREEN_REPRODUCIBILITY_BUNDLE.zip**, **38** files, SHA-256 **`2f5e4ab91919724f29c906c41c95baf27b867c39d723ca7b113c3ff8e02d5069`**. Contains exact **four executed Python scripts**, stage1 full 123-case result JSON, seven-month six-rule locked result JSON (all 7 months), full original Jan2 unpaired matching audit & extracted entry markers, **434-assertion independent QA** report, legacy source modules, original event source-ordinal feature caches, the historical selected teacher pair ledgers, complete quoted-file source SHA manifest, and compact readable investor report. The seven user-provided compressed RAW monthly Dukascopy market sources remain separate and are identified by SHA; no synthetic market source substituted. Bundle ZIP CRC and included hashes passed. Main source hashes:
- Stage1 `BETA032_17D5_STAGE1_SCREEN.py`: `4dc3fcf857a6f9061fe37cec23b7b41eee7c541350cd7e95033f218d0b40d4e0`
- Seven-month `BETA032_7MONTH_LOCKED_RECHECK.py`: `bffe572741c487d92f327cfb5a73a1c492a16cbdec08800eec31d77c99744b8b`
- Independent `BETA032_INDEPENDENT_QA.py`: `c4f9e0857e08fb086335c9b6d6873767257bb5fa772eee6b21fa1a831db6c4`
- `BETA032_SOURCE_MANIFEST.json`: `0faaf8e9e738df566334c7b7be4d28534af0712132d3c73d38ef7c37a3e08d63`
- Full results `BETA032_7MONTH_LOCKED_RESULTS.json`: `b421b2799dc62c13b78faa87a49388c0889e7c75e7fc0e9ebc3e0d97dabaac0b`

**Audit passed 434/434 identity/chronology/accounting assertions.** Does NOT establish BETA005 17-layer materialized source feature parity, native MQL5 compile or fills, Coinexx 17.5-day **full-original** logger alignment, BETA015 funded risk or broker profitability.

## Expanded GitHub + multilingual research source roster

Actual source inspected via GitHub connector (as source code, not performance claim):
- `quantwrench/mt5-breakout-ea/BreakoutEA.mq5` blob `a75e4b9b472599f71198b59434b14875a43abdff`: MQL5 one-position/ATR stop/trail pattern; do not import risk-percent sizing. https://github.com/quantwrench/mt5-breakout-ea/blob/main/BreakoutEA.mq5
- `Piardian/TrendFlowing-Forex-EA/src/TrendFlowing.mq5` blob `46219a1a1ee2e518d73d61ca11ef4865806168b1`: source-separated structure/sweep/setup/trailing/risk, EURUSD/GBPUSD reports not relevant proof for XAU tick alpha. https://github.com/Piardian/TrendFlowing-Forex-EA/blob/main/src/TrendFlowing.mq5
- `edwardclewer/tick_backtest/README.md` blob `06eaebf6d9dfc879491253222225d982b21e3bee`: deterministic replay/hash logging provenance, no transferable alpha. https://github.com/edwardclewer/tick_backtest
- Public MetaQuotes break→retest→rebreak FSM: https://www.mql5.com/en/articles/18486 . R9 and Gold Hunter V8 provenance stay historical research leads. License + full source disclosure + causality gate required for all community formulas. Existing TradingView/Reddit/ForexFactory/Myfxbook and Chinese/Japanese/Korean sources remain approved as REPRODUCIBLE logic only.

## Next bounded task
Stop further tiny grids on the rejected wait+direction-flip family. Return to *qualitatively different* early accepted-break versus first-retest event-family routing; compare matched opportunity cohorts and true latest-tick fills, then separately state-conditioned early-failure exits and sustained runners. Use same 17.5d first screen, 10% strict rule / preferred 20% leap, release only frozen winners to full Jan–Jul, and require integration under BETA015 before any prospective EA promotion. August SEALED. Approved beta EA **null**, MQL5 owner permission **not given**, first incomplete infrastructure **BETA005 17-layer feature cache parity**.

***This is a completed negative scientific result, not a prediction or promise.***
