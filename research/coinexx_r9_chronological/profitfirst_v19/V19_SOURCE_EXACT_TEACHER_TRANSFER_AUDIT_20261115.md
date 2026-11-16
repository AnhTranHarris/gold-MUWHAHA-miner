# V19 — REAL Coinexx M1 two-leg cycle transfer into micro180 (source-exact pilot)
**2026-11-15 | Research-only | original EA untouched | no quote regeneration | no broker orders**

## Objective, source fidelity, and comparison
The archived MT5 M1 R9 HybridGate tester teacher reports **272,352 completed trades, +$360,693.05, 79,865 same-minute opposite-direction second legs, +$161,362.47 from those legs**. Its lineage includes synthetic tick paths, so this is a *teacher*, not an executable PnL claim. Source-exact Python baseline is `coinexx_r9.r9_baseline.R9HybridGateBaseline`, 0.01 lot, minute bracket midpoint ±$0.15, ten completed observed 1s bars for directional quality, completed M5 ATR gate, first observed Bid/Ask stop crossing, original $0.10 activation / $0.03 trailing / $0.30 initial stop, rearm opposite side. Source receipt checked by SHA-256 on **existing** original Coinexx monthly CSV.gz, no tick warehouses or synthetic bars persisted.

Selected 6 source windows were preidentified from the synthetic teacher profitable clusters and later session contrasts (not unbiased sampling):
Jan29 17–18, Feb02 daily, Mar19 10:49–19:35, Jul24 08–18, Aug20 08–18, Sep10 08–18, clock as original Coinexx source. 2h past-only source warm-up for M5 ATR and S1 state where available. **1,550,670 source quote rows** total within windows; only selected historical periods tested, not the full nine-month account ledger.

### Real source vs synthetic teacher, executed-side cost

| Window | Synthetic teacher trades / $net | Frozen R9 Python real quotes trades / $net | V19 2-leg + causal trailing trades / $net | V19 minus R9 |
|---|---:|---:|---:|---:|
| Jan29 hour | 84 / +1,327.13 | 40 / −6.39 | 40 / −14.16 | −7.77 |
| Feb02 day | 2,190 / +11,615.25 | 1,459 / −248.87 | 1,389 / −189.90 | +58.97 |
| Mar19 window | 882 / +3,049.34 | 681 / −120.73 | 650 / −97.70 | +23.03 |
| Jul24 window | 416 / +327.84 | 607 / −112.08 | 585 / −110.16 | +1.92 |
| Aug20 window | 641 / +600.15 | 689 / −186.83 | 662 / −179.78 | +7.05 |
| Sep10 window | 722 / +863.67 | 705 / −151.69 | 669 / −139.45 | +12.24 |
| **Total** | **synthetic only** | **4,181 / −826.59** | **3,995 / −731.15** | **+$95.44** |

**Trade-volume preservation 95.5513%** of same-window source benchmark, improved modeled cash in **5/6** source windows. Net win share **36.471%**, complete candidate still **negative**. Cost scenario includes actual quoted Bid/Ask and **assumed $0.02 per round trip** from archived tester fee, not broker-confirmed; additional $0.20 fee gives **+$128.92 incremental** (different trade-count); further assumed 2c price slippage each side gives **+$102.88 incremental**. Neither implies net profit or verified execution. **DO NOT promote to MT5.**

### Causal V19 policy from winning cycle research
- Preserve original R9 v1.90 minute breakout, causal S1 quality, M5 ATR gating, initial protective stop, 30s timeout, no aggressive accumulation.
- Restrict maximum 1 same-minute **opposite** rearm, hence two legs maximum.
- At the actual source tick of an accepted entry, read *already-completed M5 ATR*; if ATR >= **$8/oz**, freeze a **$0.25 trailing distance** for this position; else retain original $0.03 trail. Original $0.10 favorable activation remains. No later ATR lookahead or per-quote mode switching. These are **research priors**, not production-optimal fitted parameters.
- Daily logger replays and exact-ordinal unit tests separately show the policy is reproducible. Still fails profitability release gate.

### REAL MT5 TickLogger triangulation
Read only **four existing archived daily REAL TickLogger gz files** from Google Drive (Jan29/Feb02/Mar19/Jul24; ~38MB total). The February 2 logger has **594,529 row-by-row time_msc and integer-cent Bid/Ask matches** with original Coinexx broker export; `REAL` indicates tester real-tick input, **not live fills**. Use FIRST subsequent source quote reflecting flat position after prior position to reconstruct close as observation, **not proof of actual server deal price**.

- **Jan29 selected hour:** logger **40 trades**, baseline Python **40**; **40/40 exact entry and exit source quote ordinals/prices**, fee-based net −$6.39.
- **Feb02 day:** logger 1,475 trades, source-faithful Python 1,459; Python entries match **1,459/1,475** original logger events, **1,452 exact exit events**, 16 unmatched due logger/ATR initial warm-up/state.
- **Mar19 window:** logger 681, Python 681; **681/681 exact entry time**, **676/681 exact exit**.
- **Jul24 window:** logger 595, Python 607; all **595 logger entries matched**, **575 exact exits**, 12 Python-only entries.
- Verified logger contains same-minute profitable second legs (96 Feb02, 38 Mar19, 19 Jul24, 1 Jan29 in tested windows), but **whole-day/window real quote PnL remains negative**. This demonstrates the original synthetic high-profit teacher does not transfer as-is.

### Profitable real-quote cycles to reverse-engineer
In six V19 source windows, **3,148 entry-minute cycles**, of which **1,112 positive** (+$718.79 from positive cycles alone), **847 two-leg minute cycles**, **199 positive two-leg minute cycles**; **735 active five-minute blocks**, **170 positive** (+$284.28 from those positive blocks only). These are **hindsight labels**, not selective trading returns. Their complete PnL including negative cycles is V19 −$731.15. Source-exact derived ledgers identify past-only phase, session, ATR, quote spread, rearm side, and actual quote-ordinal lifecycle.

### Micro180 exact source-clock alignment and collision protocol
- Existing original V9 micro180 entry ordinals cross-indexed against **strictly earlier logger rows** for Jan29, Feb02, Mar19, Jul24, with **3,897/3,897** historical V9 entries assigned latest prior REAL R9 phase: BOTH_ARMED, REARM_OPPOSITE aligned/opposing, POSITION_OPEN, WAIT. **All large phase groups have negative modeled net**, under both 2c and 20c assumed fee; no phase-only gating licensed.
- On **first 135,948 February 2 quote rows**, frozen original V9 run in parallel with an additional **V19 read-only shadow**: identical **318 V9 entries and 318 V9 exits**/event chronology; V19 independently sees 235 cycle entries and 656 quote-level simulated inventory-collision states (NOT 656 trades). The shadow can detect netting/account-collision questions but never changes V9 orders, entry/exit, governor or protective stops.
- Source policy file `causal_cycle_policy_v19.py`, synthetic tests `test_causal_cycle_policy_v19.py` and immutable original R9 v1.90 / V9 source hashes. A full February 2 frozen V19 class vs independently implemented source runner produced exactly the same **1,389** entry/exit ordinals and prices. No MQL5 V19 implementation.

## Scientific status & next trading-cycle gate
- This is a **small targeted real-quote pilot**, not full Jan–Sep V19, not true untouched OOS, not broker live/demo fills, not MT5 MetaEditor compile or native/Python parity.
- Reproduce/select **positive cycle signatures before the next entry**, not by their future net outcome. Derive actionable micro180 state policy only if future-only matched source-sequence rearming earns **positive complete after-cost net, >50% winners, >=95% volume** and acceptable monthly/tail risk. Avoid blindly using teacher's synthetic-winning second-leg timing.
- Actual Coinexx MT5 logged deal timestamps, spread at request/fill, stop-modification success/cost and account netting/hedging constraints remain essential for broker qualification. Preserve no-trade/abstention and original risk guards in research.
- Current evidence **supports preserving the multi-regime, multi-session, multi-trend minute-cycle mechanism as a research candidate**, not claiming the archival +$360k is replicated.

## Reproducibility
Research files `teacher_cycle_replay.py`, `real_logger_cycle_validate.py`, `causal_cycle_policy_v19.py`, `test_causal_cycle_policy_v19.py`, `micro180_cycle_alignment.py`, `check_v19_micro180_parity.py`, `build_v19_positive_cycle_map.py`, `build_v19_cycle_receipt.py`, `verify_v19_cycle_receipt.py` are packaged with the local conversation evidence archive. The ZIP contains only **derived small source and outputs** (selected-window trade ledgers, matching receipts, as-of states, model variants) and **NO original 576MB Coinexx quotes or 4 RAW TickLogger days**. The original V9, original MQL5 and original source baseline remain untouched.

Reference MT5 M1 teacher [PR #55](https://github.com/AnhTranHarris/gold-MUWHAHA-miner/pull/55), and original provider docs [MT5 synthetic real tick generation](https://www.metatrader5.com/en/terminal/help/algotrading/tick_generation), [MQL5 trade event callbacks](https://www.mql5.com/en/docs/event_handlers/ontradetransaction).
