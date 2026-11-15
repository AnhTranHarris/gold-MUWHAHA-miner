# R9 V13 — Causal Fibonacci–Anchor Execution Lattice (profit-first Python study)
**2026-11-15 | RESEARCH ONLY | parent V12 immutable | no native EA code or orders**

## Objective and scope

Build and test a cost-aware Fibonacci/quote-duration-anchor/EMA/SMA **virtual entry lattice**, using the original full January–September 2026 Coinexx ordered quotes and frozen V12 original basket-entry event ledger. The objective is **positive net expectancy after executable Bid/Ask and an additional $0.20 modeled cash/trade, sustainable frequency and a majority of profitable completed trades**. None of the configurations met the profit objective; nothing is promoted as a production setting.

**All nine original monthly SHA-256 pins verified**. Original quotes processed: **72,129,347**. Frozen V9 on-policy baseline: **338,065 entries, 338,064 closed, 128,203 historical profitable trade outcomes (37.92%)**. Original R9/V8/V9/V10/V11/V12 code is untouched.

## What was tested

The standalone Python study constructed M1 **EMA9/EMA20**, M5 **SMA12/SMA20**, separately confirmed M1/M5 pivot Fibonacci rails requiring two fully completed right bars, a session quote-**duration**-weighted price anchor (TWAP proxy, **not traded-volume VWAP**), an observed preceding 180-second quote-range lattice, and counterfactual market-side pullback-and-rebound entry after each frozen V9 signal. Observed execution quotes remain ordered by original source ordinal, even for same-millisecond records. A candidate must touch its frozen rail and show 250ms plus two subsequent source quote updates of rebound before market-price entry; **no free passive limit fills, martingale or averaging down**.

| Nine full months | Completed alternative fills | Positive trade rate | Modeled net total | Net/trade | Positive months |
|---|---:|---:|---:|---:|---:|
| Fib 23.6%, observed micro180 extreme | 57,430 | 38.97% | −$22,353.14 | −$0.3892 | 0/9 |
| Fib 38.2%, observed micro180 extreme | 43,383 | 38.77% | −$16,918.51 | −$0.3900 | 0/9 |
| Fib 23.6% **signal-anchored** virtual step | 38,214 | 40.41% | −$14,388.51 | −$0.3765 | 0/9 |
| Equal fixed 25-cent step control | 58,021 | 40.09% | −$22,009.60 | −$0.3793 | 0/9 |
| Fib 38.2% plus 10-minute, $3-target, $1-stop structural research hold | 32,353 | 25.80% | −$12,272.99 | −$0.3793 | 0/9 |

The strict confirmed M1/M5 swing/Fib0.382/0.5/0.618 confluences produced **fewer than 45 completed positions per month** in the three pilot months, inadequate for desired throughput and also not net-positive. Additional micro quote-time-anchor checks and EMA9-versus-EMA20/SMA12-versus-SMA20 comparisons did not pass the cost hurdle.

**Entry winner map:** 65,935/128,203 (51.43%) historical winners occurred at the top 80–100% of their directional past-observed 180-second range. That bucket still averaged **−$0.4022/trade**, because most candidate signals — both winning and losing — occurred there. The single limited-complexity histogram gradient boost (Jan–Apr fit, May–Jun calibration, Jul–Sep later check) achieved **later-month AUC 0.536** for the original V9 winner label; a frozen calibration top-1%-ranked subset still averaged **−$0.4040** net. Training-only positive selection did not generalize.

## Very important qualification

This is a **chronological V9 signal-cohort intervention**, not a newly executable strategy with the complete V9 rearm/cap routing regenerated. Alternative entry/exit timing would itself change which future V9 signals occur. No alternative strategy's summed PnL can yet be called full-account on-policy performance. Simulated fills are market-side observed quotes **without** actual Coinexx execution latency/slippage/rejections; once real costs are added, results may deteriorate.

All Jan–Sep months have been used in project R&D; the later chronological check is **not untouched true OOS**. The Python runner and 30-file small evidence ZIP (no tick sources) were provided as conversation artifacts:
`R9_V13_CFAEL_Causal_ProfitFirst_Python_Research_20261115.zip` — SHA-256 `5dfba7464ef322fde40aeed4a878946dc422898f826bd2c588dd1bcc2014d7f1`.
It includes the tested research source, five source-order/quote-side unit contracts, all compact 9-month result JSON, and a comprehensive source-specific report. **The ZIP is a conversation attachment, not a blob stored in GitHub; it is not present in this repository.** No raw tick archives or large per-trade feature snapshots are copied to GitHub/Drive.

## Profit-positive next decision

**Stop tuning these already-failed V9 micro-breakout entry cohorts.** A productive next test is a truly new independent **M15/H1 confirmed structural-pullback specialist**, with micro180 acting as a *secondary timing and spread-quality trigger*, not the primary predictor. Pair a large enough structural target with a frozen behind-entry structural stop and model actual executable sides. First source-exact Python pilot, then a full **closed-loop** new strategy replay with its own signals and risk governor; require positive monthly expectancy, acceptable tails, meaningful throughput and later untouched validation. Only then discuss translating parameters to MT5 and obtaining DEMO fill telemetry.

Research motivation (not evidence of strategy profitability): FRBNY Osler FX support/resistance and stop cascades; BIS OTC FX market fragmentation and execution-algorithm risks; Lalor/Swishchuk 2024 market-simulation adverse selection. See exact references in the conversation report.

**No MT5 EA is created or deployed in V13. Keep this research branch unmerged.**
