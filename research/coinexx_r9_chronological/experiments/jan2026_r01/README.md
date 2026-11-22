# R9 January 2026 — REAL-tick reconstruction R01 (research-only)

**Status: FAILED acceptance gate. No EA deployment or policy approval.**

This isolated branch descends from `carson/coinexx-r9-chronological-backtest-v1-20261112` (commit `de3e61702759af67f93eb12cff01084789357645`). It **adds** a C++17 chronological state-machine replay, bounded 25-configuration exploratory screen, exact sparse one-to-one alignment scorer and four tests. Original `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`, July R8 and S100 V2 are unchanged.

## Source pins

- Original MQL5 v1.90 blob: `7eecb5f1947017a01ce85b2520725de54749e523`
- Original January Coinexx broker-export gzip SHA-256: `1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`
- Original R9 SYNTH fixed-trade book SHA-256: `9c9ebf5889c309a10e4370e355b99d75ae54cf5ccfdaa5ebab9042206f3f8cc5`
- Preserved full R9–REAL quote-risk merge SHA-256: `c60dfe6a9882c3ae23e55080106444c33439bf090a298206d3afb73387e02c53`
- Source January 27,980-row manifest: member `2026-01_ALL_27980_TRADES_manifest.csv` in the already-saved January metrics ZIP: https://drive.google.com/file/d/1CHCXeBYDDQSI9PiZ06TfWy1xUlEpPQGC/view
- Full January research report: https://docs.google.com/document/d/1o1mXF2m_R2ARVNpGTRy0fMHDaD8tKvw-TGPoKigp-3A/edit

## Execution

A Linux workstation with `g++ -std=c++17`, `zlib`, Python 3, `numpy`, `pandas` and `scipy` can reproduce this benchmark using the existing original Coinexx month file.

```bash
g++ -std=c++17 -O3 -Wall -Wextra -Werror -o r9_real_replay r9_real_replay.cpp -lz
./r9_real_replay /path/to/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz /tmp/r9_january_trades.csv
export R9_REAL_TICKS=/path/to/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz
export R9_REFERENCE_MANIFEST=/path/to/2026-01_ALL_27980_TRADES_manifest.csv
python score_alignment.py /tmp/r9_january_trades.csv /tmp/baseline_score.json
python -m unittest verify_replay -v
python run_screen.py 0 25
```

The replay reads each original input row once, preserves equal-millisecond source-order ticks, does not synthesize missing quote data, builds observed completed 1-second/M5 ATR states causally, and writes independent BUY Ask/SELL Bid executions. Synthetic reference timestamps and original booked profits are **not loaded into the live replay**; the reference manifest is used only by the post-hoc alignment scorer.

## Exact baseline parity

`7,699,274` quote records, 413 equal-millisecond adjacent pairs, 32,179 REAL replay entries (31,498 stop, 681 timeout), 31,487 rearms, 39,540 trailing updates, identical to the preexisting January Python receipt. Distinct C++ results: 14,080 positive, 17,950 negative and 149 flat liquidation-side closes, total **−$6,053.12 price-dollar equivalents per one ounce**, before commission/slippage/funding, **not** realized account P&L. All four tests pass: pinned original hash; full source-receipt parity; sparse one-to-one exact matching; future suffix cannot modify historical prefix events.

## January acceptance criteria and observed failure

Original January reference: 27,980 trades, 24,368 positive booked exits. The user requires at least both these counts, plus entry/exit correspondence within 5% tolerances. For this initial fixed-clock evaluation, a strict ±2-second dual-endpoint tolerance was measured; other time windows were also recorded.

| R01 candidate | Generated trades | Positive REAL closes | Original matched entry+exit ±2s | REAL quote-dollar total / one oz |
|---|---:|---:|---:|---:|
| source-faithful R9 | 32,179 | 14,080 | 441 (1.58%) | −6,053.12 |
| widen stop to 100 points | 30,098 | 17,591 | 488 (1.74%) | −5,972.12 |
| permissive eff 0.0 / range 30 | 60,288 | 27,154 | 1,004 (3.59%) | −10,463.78 |

**No candidate passes all goals; every one of the 25 screened variants has negative pre-cost REAL quote P&L.** Do not promote the variant with 27,154 positive exits: it doubles trade volume, still fails the entry/exit correspondence requirement, and worsens whole-system economics.

The frozen original fixed-window quote-envelope upper bound is 21,464 observed positive MFE on 27,025 complete windows; even assuming all 955 UNKNOWN windows could have become positive gives at most 22,419, less than 24,368. It is necessary to research independent causal entry and exit timing, not merely profit taking at the original time labels.

## Next scientific gate

1. Extend the source-exact R9 event-state forensic: original minute bracket, completed S1, completed ATR, spread, session, position state, conditional same-minute rearm; grade reason codes on each original time anchor **without feeding the anchor into entry decisions**.
2. Match original negative-cycle runs against the separately protected positive/recovered controls. Freeze alignment metric and causal feature definitions before fitting.
3. Propose a new independently executable, structure-aware entry/hold/exit router; preserve full trade distribution and account risk, not only high-volume count.
4. Test frozen alternatives on February and later REAL Coinexx months, with quote gaps, spread, stop crossing, latency and execution-cost stress; no optimization on holdouts.
5. Modify MQL5 in a separate candidate only **after** a complete research successor meets the owner gate. No historical SYNTH price data, future labels, prior fallback code or raw tick duplication.

The `screen_results.jsonl` includes all 25 attempted variants, not only the most flattering ones.
