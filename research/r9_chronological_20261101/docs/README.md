# R9 Minimal Chronological Replay — January 2026

**Status:** January Coinexx source-level ENTRY+EXIT PARITY ACHIEVED FOR 31,745 EXACTLY MATCHED TRADES; NOT 100% FULL-STREAM PARITY. Frozen January Dukascopy shadow replay completed. **Not authorized for live trading.**

## Original code provenance

- Repository: `AnhTranHarris/gold-MUWHAHA-miner`
- Branch: `carson/mt5-r9-hybrid-gate-certification`
- Pinned parent commit: `8729a6345655a7b4ea31facc81982004ee2b8921`
- Pinned MQL5 source blob: `7eecb5f1947017a01ce85b2520725de54749e523`
- Source: `Experts/GoldMuwahahaMiner_R9_HybridGate.mq5`
- R9 tester variant: `GoldMuwahahaMiner_R9_TickLogger`, same parameters with tick logger enabled.

## Input data (already archived in primary Drive)

Coinexx raw January (source clock UTC+2):
- `XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz`
- Drive ID: `1mSIbKZYuhtqza05ro8kbb4MfhAjUVkvP`

Dukascopy raw January (UTC native):
- `XAUUSD_DUKAS_2026_01_ticks.csv.gz`
- Drive ID: `1DyKXj-DDhsP3eMXm0j7QQimXRLoHSHKo`

MT5 real reference report:
- `ReportTester-871471_jan2026_jul2026_R9_ticklog_real.xlsx`
- Drive ID: `1XofN5m44GU4RgfrjhGHZoK1uaQpGRJgq`

**No raw market data was modified or reuploaded.**

## Fidelity

The replay mirrors R9's chronological quote-bucket completion, internal per-minute midpoint boundaries, spread gate, completed M5 ATR(14), session ATR gates, S1 displacement/efficiency/range/turn logic, market-entry sides, quote-side initial stops, trailing stop modifications, tick-only max-hold closes, and one-tick post-exit opposite-side rearm. It deliberately reproduces the current R9 rearm flaw, because this is a baseline, not a fix.

MT5 executes attached stops and trade-server operations. Python uses source bid/ask at the triggered quote and assumes stop modifications are accepted, fixed $0.01-per-side commissions, Coinexx point/tick size $0.01 and minimum broker stop level 0. These are **execution-model assumptions**, not verified broker metadata. Margin and stop-out are not modeled; the $100,000 run is a source/logic parity experiment.

The MT5 tester has pre-Jan M5 history; the raw January file does not. Jan 2 initial setup is therefore not directly replicable. Exact-second parity is scored after `2026-01-02 03:00:00` broker time. The all-January trade lifecycle parity also includes matched trades before that cutoff when any occur.

## January results

| Measure | Coinexx MT5 reference | Coinexx Python | Dukascopy Python frozen |
| --- | ---: | ---: | ---: |
| January entries | 31,915 | 32,380 | 289 |
| January closed net USD | -6,651.62 | -6,770.92 | -97.38 |
| Ticks processed | reference is 7-mo report | 7,699,274 | 9,135,062 |

**Exact MT5 lifecycle matched:** 31,745 / 31,915 = 99.4673% of January MT5 trades. Each matched trade has the same entry second, entry direction, entry price, exit second, exit price, exit reason, and USD net result. The remaining 170 MT5 trades were unmatched, while Python emitted 635 extra trades. This is **near-exact lifecycle parity on the common trade population**, not full 1:1 parity on the entire tick stream.

After excluding Jan 2 before 03:00 native broker time: 31,735 / 31,791 (99.8238%) reference entries match a Python entry in the exact second and same direction, with 31,702 of those having an exact entry price. 31,745 full-lifecycle matches are computed separately, anchored on exact entry second+direction+price, across the whole month.

Of 31,745 fully matched trades, the net P&L is -$6,617.72 for both MT5 and Python. The extra 635 Python trades contribute -$153.20. The unmatched 170 MT5 trades contribute -$33.90, explaining the $119.30 headline difference.

**Dukascopy:** 9,126,821 candidate evaluations were blocked by the frozen 25 Coinexx-point spread ceiling. This is source/broker transfer failure of opportunity supply, not proof of a universal failure of the underlying signal. The Dukascopy price archive uses 1/1000 price scaling and UTC timestamps. The frozen EA's `InpQuoteUtcOffsetMinutes=0` is intentionally unchanged. The Dukascopy UTC source clock is **not** Coinexx's +2 hour server clock, so time-of-day gate effects are not like-for-like without a later explicit clock-interface test. The Coinexx 0.01 quote-point specification is deliberately applied to Dukascopy for a fixed-parameter transfer experiment; this does not claim Dukascopy is an executable Coinexx account.

## Files

- `src/r9_replay.py`: chronological raw-tick replay.
- `src/extract_mt5_january.py`: streaming extraction from large MT5 XLSX XML.
- `src/compare_mt5.py`: trade-by-trade entry parity.
- `src/compare_exits.py`: exact lifecycle parity.
- `tests/test_unit.py`: replay unit tests.
- `results/coinexx_reference`: extracted Jan MT5 order/deal rows.
- `results/coinexx_january`: Python Coinexx entry and exit ledgers/summary.
- `results/dukascopy_january`: Python Dukascopy entry and exit ledgers/summary.
- `results/coinexx_parity.json`, `results/coinexx_exit_parity.json`: exact matching evidence.

## Run

```bash
python -m unittest discover -s tests -v
python src/extract_mt5_january.py /path/to/ReportTester-871471_jan2026_jul2026_R9_ticklog_real.xlsx --out results/coinexx_reference
python src/r9_replay.py --ticks /path/to/XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz --source coinexx --out results/coinexx_january
python src/compare_mt5.py --ref results/coinexx_reference/january_deals.csv --replay results/coinexx_january/entries.csv --out results/coinexx_parity.json
python src/compare_exits.py
python src/r9_replay.py --ticks /path/to/XAUUSD_DUKAS_2026_01_ticks.csv.gz --source dukascopy --out results/dukascopy_january
```

## Next decision

**Do not advance to February yet.** To reach strict full-stream parity, investigate the 170 unmatched reference entries and 635 excess Python entries, especially broker trade rejections, position-state reconciliation, nonzero stop/freeze level, and MT5 `OnTick` coalescing. Do not change the strategy's entry/hold/exit logic to force historical matches; resolve only demonstrated simulator differences, version them, and retest January before using the engine for strategy optimization.
