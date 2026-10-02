# DELTA 003 — Coinexx MT5 R9 Execution-Parity Calibration Report

**Status:** VERIFIED_DURABLE  
**Parent:** `DELTA_002_DUKASCOPY_TICK_LAB`  
**Strategy optimization:** NONE  
**August 2026:** SEALED / NOT ACCESSED

## 1. Objective

Calibrate the DELTA Python tick laboratory to the preserved Coinexx MT5 R9 REAL execution/accounting behavior before any new candidate research.

DELTA_003 does not alter the R9 strategy and does not tune a candidate. Its only job is to reproduce the known R9 Coinexx state machine and economics closely enough that later research can distinguish:
- a Python implementation error;
- a broker/execution difference;
- a genuine market-path/feed difference.

## 2. Evidence used

Authoritative surfaces:
- R9 REAL Coinexx Strategy Tester report;
- validated R9 REAL TickLogger daily corpus;
- DELTA-owned R9 MT5 functional summary;
- DELTA_002 verified Dukascopy tick lab.

The validated REAL TickLogger corpus contains 56,608,185 ticks in 149 daily files, with zero run-label mismatches, zero timestamp/date mismatches, zero monotonic decreases, all daily gzip files validated, and Drive audit passed.

## 3. Frozen Coinexx execution economics

Recovered from R9 REAL evidence:

- broker/company: Coinexx Limited;
- tester server: Coinexx-Demo;
- MT5 build: 6182;
- symbol: XAUUSD;
- account currency: USD;
- diagnostic balance: $100,000;
- leverage: 1:500;
- fixed lot: 0.01;
- symbol display/working precision: 2 decimals;
- point price: $0.01;
- observed trade tick size: $0.01;
- inferred contract size: 100 oz per 1.00 lot;
- 0.01 lot therefore represents 1 oz;
- $1.00 XAUUSD price move at 0.01 lot = $1.00 P/L;
- BUY market entry uses Ask;
- BUY mark/exit uses Bid;
- SELL market entry uses Bid;
- SELL mark/exit uses Ask;
- entry commission at 0.01 lot = -$0.01;
- exit commission at 0.01 lot = -$0.01;
- round-trip commission = -$0.02;
- protective stop fills at the first executable quote after the stop is crossed;
- R9 deviation input = 20 points.

The commission model is not an approximation. It is recovered directly from the tester deal ledger.

## 4. MT5 deal-accounting convention

The tester's gross-profit/gross-loss accounting is deal-based.

At entry:
- the -$0.01 entry commission is booked immediately to balance and gross loss.

At exit:
- raw price P/L is calculated from executable Bid/Ask;
- -$0.01 exit commission is applied;
- if raw price P/L is positive, the exit deal contributes to gross profit;
- otherwise the exit deal contributes to gross loss.

This convention exactly reproduces the R9 REAL report.

## 5. R9 OnTick ordering recovered

The calibrated Python state-machine order is:

1. broker-side protective stop processing against the current executable quote;
2. completed-second state visibility/update;
3. new-minute reset and virtual bracket freeze;
4. if a position is open:
   - mark the position as observed by R9;
   - evaluate 30-second maximum hold;
   - if still open, evaluate trailing;
   - return from this OnTick branch;
5. if a previously observed position has disappeared:
   - process opposite-side same-minute rearm;
   - return;
6. otherwise evaluate one new bracket crossing/entry opportunity.

### Critical observation latch

R9 does not rearm merely because an order was opened and then closed.

A newly opened position must survive to a later OnTick where R9 actually observes it as open. Only after that observed position later disappears can the same-minute opposite-side rearm occur.

Therefore:

`ENTRY -> broker stop before next OnTick`

does **not** arm a re-entry.

This subtlety was necessary for exact event-stream parity.

## 6. Full January parity

Calibration was replayed across all 21 preserved January REAL TickLogger daily files.

- logger rows: **7,699,274**
- event mismatches: **0**
- event-count aggregate mismatch: **0**
- trades: **31,915**
- winning trades: **13,947**
- losing trades: **17,968**
- gross profit: **$3,785.28**
- gross loss: **-$10,436.90**
- net profit: **-$6,651.62**

These metrics exactly equal the frozen MT5 R9 REAL January reference.

### January 2 detailed check

- rows: 341,569
- event mismatches: 0
- trades: 1,525
- wins: 717
- losses: 808
- gross profit: $158.01
- gross loss: -$461.97
- net: -$303.96
- maximum balance drawdown: $304.28
- reconstructed maximum executable-side equity drawdown: about $304.47
- average hold: about 7.256 seconds

## 7. DST/summer cross-check

R9 REAL July 1 was replayed independently after both US and UK daylight-saving transitions.

- rows: **338,441**
- event mismatches: **0**
- trades: 1,535
- wins: 700
- losses: 835
- gross profit: $162.26
- gross loss: -$462.09
- net: -$299.83

This verifies that the calibrated session/DST path is not merely a winter-January fit.

## 8. Native Dukascopy is a different spread surface

DELTA_002 preserves Dukascopy's actual Bid/Ask quotes. DELTA_003 deliberately does not rewrite them.

### Coinexx January

All logger ticks:
- median spread: **$0.19**
- 10th percentile: $0.19
- 90th percentile: $0.35
- **87.07%** of ticks are at or below R9's $0.25 spread gate.

R9 entries:
- median spread: **$0.19**
- 90th percentile: $0.21
- maximum entry spread: $0.25.

### Dukascopy January

- median native spread: **$0.70**
- 10th percentile: $0.54
- 90th percentile: $1.36
- only **0.0476%** of ticks are at or below $0.25.

Running unmodified R9 against the native Dukascopy quote surface therefore produces only:
- 289 trades;
- 109 winners;
- 180 losses;
- +$35.836 gross profit;
- -$133.233 gross loss;
- -$97.397 net.

That is **not** interpreted as an R9 state-machine failure. It is a broker/feed-surface difference.

## 9. Two surfaces are now explicit

### COINEXX_PARITY

Purpose:
- reproduce R9 MT5 state and accounting;
- validate the Python engine;
- recover broker/economic rules.

Authority:
- preserved R9 REAL logger/report.

### DUKAS_NATIVE

Purpose:
- independent causal cross-broker robustness;
- preserve original Dukascopy Bid/Ask chronology and spread.

It is not silently altered to make its trade count resemble Coinexx.

A future Coinexx-like quote/spread overlay on top of the Dukascopy mid/path must be a **separate preregistered modeled surface**. It cannot be mislabeled as raw Dukascopy.

## 10. Unresolved broker properties

The preserved evidence does not uniquely determine:
- exact `SYMBOL_TRADE_STOPS_LEVEL` points;
- exact `SYMBOL_TRADE_FREEZE_LEVEL` points;
- exact filling-mode enum;
- margin stop-out mode/level;
- commission scaling at lot sizes other than 0.01.

These remain explicitly unresolved rather than invented.

The calibration tapes show that R9's configured $0.30 initial stop was not enlarged in the observed parity cases.

## 11. Durable implementation

Canonical DELTA files:
- `research/delta/lab/coinexx_r9_adapter.py`
- `research/delta/lab/r9_parity_runner.py`
- `research/delta/reference/DELTA_003_COINEXX_EXECUTION_CONFIG.json`
- `research/delta/qa/DELTA_003_COINEXX_R9_PARITY_QA.py`
- `research/delta/checkpoints/DELTA_003_PARITY_QA.json`

The adapter contains:
- exact logger-oracle execution/state replay;
- recovered MT5 deal accounting;
- standalone causal R9 reconstruction from raw ordered Bid/Ask arrays;
- 2026 London/New York DST logic;
- direct compatibility with DELTA_002 month memmaps.

## 12. Scientific conclusion

The DELTA Python environment can now reproduce the preserved R9 Coinexx behavior exactly on a full calibration month and on a summer/DST cross-check day.

The remaining difference between a Coinexx R9 run and a Dukascopy R9 run is therefore no longer allowed to be described vaguely as "Python versus MT5." The project can now separate:
- state-machine parity;
- accounting/execution parity;
- quote/feed/path differences.

That separation is the required foundation for the next research stage.

## 13. Next engineering unit

The next unit should build an explicitly modeled **Coinexx-like research quote/execution surface over the independent Dukascopy path**, while retaining DUKAS_NATIVE unchanged.

That unit must:
- remain separately labeled from raw Dukascopy;
- derive its spread/cost model only from causal Coinexx evidence;
- preserve Dukascopy directional chronology;
- avoid fitting to SYNTH outcomes;
- quantify sensitivity across plausible Coinexx spread/cost assumptions;
- keep August sealed.

No candidate MQL5 translation is authorized by DELTA_003.
