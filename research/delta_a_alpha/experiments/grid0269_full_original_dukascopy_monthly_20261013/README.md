# GRID0269 — COMPLETE January–July original Dukascopy tick-level Python V1 QA
Date 2026-10-13. **Research-only**. Active branch delta-A-alpha; original owner law and V1 frozen whitepaper control any next change. August SEALED; no trading or MQL5 conversion. **Scientific J0183 unchanged.**

## Actual executed scope

Seven independent full original-month replay processes, with exact unaggregated ordered Dukascopy Bid/Ask ticks; complete current `research/delta_a_alpha/implementation/` FourSessionV1 stack from GRID0268; no R9 OVERFIT teacher leakage, no Coinexx MT5 report audit, and no fabricated real broker fills.

Fixed identical monthly config: initial hypothetical cash **$100,000 EACH month**, fixed 0.01 lot (100 oz/lot), assumed leverage 1:500, $0.20 assumed completed-trade round-trip commission, 250 ms research order latency, margin reserve 35%, global cap 2 open shadow positions, trade permissions True *as a hypothetical experiment*, no actual DEAL_ADD. No Martingale, no month-conditioning features. Months reset state, so **sum of monthly P&L is NOT a continuous funded seven-month account.**

**Exact full original-tick data rows: 57,527,562** across January through July. Original monthly SHA256 source hashes, full closed-trade chronological record, 31/30/28 per-day UTC partitions, ISO-week monthly slices, intratick quote-equity DD, original source release/evaluation counts, complete runner, V1 Python implementation snapshot and 85 regression tests are preserved in the recovery package.

## Observed monthly outcomes (USD account CASH, hypothetical)

| 2026 month | Original ticks | Closed trades | Net realized shadow | PF | Positive UTC days | Positive partial ISO weeks |
|---|---:|---:|---:|---:|---:|---:|
| Jan | 9,135,062 | 3,258 | -3,015.32 | 0.413 | 0 | 0 |
| Feb | 7,538,339 | 1,384 | -1,082.65 | 0.534 | 1 | 0 |
| Mar | 9,433,179 | 2,839 | -2,382.16 | 0.512 | 0 | 0 |
| Apr | 7,470,570 | 2,674 | -2,569.05 | 0.403 | 1 | 0 |
| May | 8,333,165 | 3,504 | -2,774.65 | 0.464 | 0 | 0 |
| Jun | 8,201,406 | 4,240 | -3,356.50 | 0.488 | 0 | 0 |
| Jul | 7,415,841 | 3,583 | -2,991.25 | 0.407 | 0 | 0 |
| **7 separate resets, sum** | **57,527,562** | **21,482** | **-18,171.576** | **0.456** | **2** | **0** |

Gross profit 15,248.073, gross loss -33,419.649, win 33.9075% across completed shadow closes. **34/34 negative partial ISO-week slices**. All 7 months negative. Full intratick DD individually in reports; month DD values must never be added as if one continuous portfolio.

**Engineering QA pass:** chronological ticks, source identity, actual full original input counts/hashes, cash/trade ledger reconciliation, and no broker-phantom deals. **Research economics fail:** no month/week positive by user goals; complete previously successful Jan/Feb/March Vertical V1 specialist frontiers not shown to be reproduced, so no inference they were lost or invalidated. This is current-code behavior, not a new strategy breakthrough. Broker-equivalent MT5 EA not certified.

## Durable owner Google Drive results

- [All 7 monthly report folders/archives/workbooks + master](https://drive.google.com/drive/folders/1qUp7EmAQSH8Mj59kmvSgBtSk0S4Ah4bq)
- [Owner human seven-month category report](https://docs.google.com/document/d/1E9e5ZjmzuSfaBr8-zLuD1FTE82CuBO1FcMrwgeixaWE/edit)
- [Complete 7-month source + months recovery ZIP](https://drive.google.com/file/d/1nBoxf4V7Tv7JjSd5Vb-9cZzw_mH3i-8s/view)

**Per month three verified items in folder:** readable daily/weekly Google Doc, worksheet tabs with daily/weekly scorecards, and lossless detailed ZIP with trade-level closed ledger and exact daily/week/month JSON/config/source hash/QA logs. Original giant raw ticks remain in established owner source storage, outside these compact derived archives.

**Forensic retry note:** initial Jan and Jun gzip-open streams threw transient EOF despite gzip integrity pass; both were rerun COMPLETELY using byte-for-byte matching local copies (same SHA-256), and all months passed whole-source reading and ledger consistency. Do not mark source invalid or fill tick gaps.

**Owner benchmark roles:** R9 SYNTH is ideal whole-portfolio daily/weekly/monthly; R9 OVERFIT ideal offline per-trade teacher; original Dukascopy tick execution is research truth. No speculative MT5 timeframe alignment work or report auditing is a blocker. Time partitions UTC.

**Next required decision:** compare accepted frozen original source and exact successful configurations against this exact current V1 source/funnel, find and repair genuinely missing/altered mechanisms, and rerun full months only after a targeted code change with QA. Do not reset original research or confuse this current-research shadow result with previous accepted frontiers.
