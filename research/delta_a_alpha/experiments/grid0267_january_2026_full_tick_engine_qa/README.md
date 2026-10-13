# GRID0267 — JANUARY 2026 FULL ORIGINAL DUKASCOPY TICK PYTHON IMPLEMENTATION QA/QC

**Scope:** Current actual `delta-A-alpha` `research/delta_a_alpha/implementation` Python engine. No EA translation, no trading enabled, no J0183 movement, August sealed. GRID0258 original control unchanged.

## Grounded input / replay

- **January original Dukascopy raw ordered Bid/Ask tick CSV.GZ:** `XAUUSD_DUKAS_2026_01_ticks.csv(3).gz`.
- Compressed SHA256: `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`; match to owner canonical January hash.
- **9,135,062 ticks processed in EACH of two full-Jan 2026 original-row-order replays**, first `2026-01-01T23:00:00.596Z`, last `2026-01-30T21:59:51.954Z`.
- Current branch source restoration: 31 GitHub source/test files recovered through source-byte-preserving Base64 transfer, verified against *exact* Git blob SHA1, plus 6 inherited nonduplicated module dependencies independently matching current Git blobs. **37 exact current-source files**, run as one implementation. [Persistent complete current-source transfer snapshot](https://docs.google.com/document/d/1zx0doJP6P4Hc0oMRAJmPpDkAnohqJR8ZipqUCpwDgUU/edit).
- Selected present tests in this extracted dependency closure: **72 / 72 passed**. This is a *subset* of the entire repository tests, not claimed exhaustive.
- No synthetic quote generation, no intrasecond look-ahead, no imported August data, exact original row chronology and Bid/Ask; real broker transaction ledger is **separate from shadow simulation**.

## Baselines (two full runs on identical January data)

| Metric | Fail-closed `DENY` | Hypothetical `HYPOTHETICAL` |
|---|---:|---:|
| Tick observations | 9,135,062 | 9,135,062 |
| Tick-by-tick feed broker permission | False | True, ASSUMED |
| Hypothetical simulated execution | No | Yes |
| Initial research USD | $300 | $300 |
| Modeled 0.01-lot completed closes | 0 | **82** |
| Net modeled USD | $0 | **−$98.771** |
| Closing modeled cash USD | $300 | **$201.229** |
| Modeled gross gains/losses USD | 0 / 0 | +29.729 / −128.500 |
| Modeled PF | N/A | 0.231354 |
| Modeled win rate | N/A | 28.0488% |
| Max quote-equity drawdown USD | 0 | 112.197 |
| Max hypothetical simultaneous positions | 0 | 2 |
| **Verified actual Coinexx DEAL_ADD** | **0** | **0** |
| Python runtime/replay error | None | None |

**Cost/contract assumptions (not Coinexx certification):** research $300 starting cash, lot 0.01, modeled 100oz/standard lot, assumed 1:500 leverage, $0.20 per completed roundtrip cost, 250ms latency, 2 open max, current hard-fail equity floor 65% of opening cash. All source fills are quote-based research transactions, never broker acknowledgment.

## February-and-beyond engineering action items from observed JAN bottleneck

Complete Jan permitted-run event counts:
- Creator-grid event emissions **456,468** (events, not trades).
- Structural opportunities **2,599,027**, matched L3 proposals **76,877**.
- L1–L6 qualified chain **64,083**.
- L7 spread-denied **23,652**, risk-halt denied **39,822** (candidate-event rejection counter).
- Funded shadow requests **89**; hypothetical fills/closes **82/82**.
- Gross negative cash and quote-DD hit capital survivability stop; this confirms risk-halt mechanics activated rather than an uncaught source parser exception.
- Deny mode yields 0 executed and 0 creator-grid raw emissions because current source router internally gates on broker_tradable; deny mode **only** proves fail-closed safety, not opportunity-count potential.
- Fully cross-checked invariants: cash + gross gains/loss reconciles; closed = filled - open; daily-funded entries/closes add to 82; both real broker ledgers report zero confirmed deals; position max respects 2-slot limit.
- Programmatic reproduction: run `qa_january_replay.py` from exact current `implementation/` with `MODE=DENY` and `MODE=HYPOTHETICAL`. Do not use `HYPOTHETICAL` findings as real Coinexx execution.

**Priority next QA:** Persist actual position/deal and per-week modeled net ledger for every exit; trace creator-crossing reject reasons and stop/target/time-exit cycles; test Coinexx REAL R9 tick and tester report parity on separately bound source with never-guessed fees/contract/clock. Confirm MT5 account metadata before EA port. Only after verified software QA resume strategy research. Do NOT infer R9 SYNTH parity (January teacher +$41,520.82 and 27,980 closes uses different tester/starting account assumptions).

**RESEARCH CLASSIFICATION:** original January market QA completion and runtime engineering baseline; **not** a profitable strategy or funded Coinexx certification. No code changes were made to the active G0 source router in this replay.
