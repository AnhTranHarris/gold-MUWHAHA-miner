# Micro180 v3 — completed first original-source comparison (FAIL)
**Date:** 2026-11-14; scope: source-native first **150,000** quotes of 2026-01 Coinexx XAUUSD; exact original gzip file `XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz`; original source SHA256 **1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8** checked. This is **IN-SAMPLE, partial-month**. No later/OOS certification. All results model 0.01 lot K=1 account currency/$1 XAUUSD move, additional C=$0.20/round trip and quote Bid/Ask spread. No MT5 fills/commission/real slippage.

| Entry profile on SAME first 150k quotes | Filled trades | Modeled net | Mean net/trade | Status |
|---|---:|---:|---:|---|
| Existing Micro180 active 5s/15s confirmation, balanced 30s veto | 274 | -$103.70 | -$0.3785 | Prior control |
| Relaxed structural + executable 15s gate | 797 | -$306.81 | -$0.3850 | Rejected |
| Relaxed sign-flipped (counterdirection) | 813 | -$329.74 | -$0.4056 | Rejected |
| Extreme throughput relaxation | 969 | -$359.69 | -$0.3712 | Rejected |
| **V3 asymmetric executable-side quant overlay** | **271** | **-$101.68** | **-$0.3752** | **FAIL positive net and volume** |
| V3 same entry, **account governor ON**, initial cash $1,000 | **81** | **-$27.32** | **-$0.3373** | **FAIL volume and net; gross risk blocks additional orders** |

V3 ungoverned 271 positions, 15 asym-score vetoes and seven missing completed-history vetoes, CVaR95 negative-trade tail about $1.06, no observed <=-$2 close in this **limited sample**; 0 profitable source days. V3 account-governed first sample: 81 positions, 1,446 projected additional order denials due to daily gross-risk capacity, $972.68 resulting modeled equity, no >=$2 observed individual completed losses in this tiny slice. A historical quote gap can still exceed the intended $2 realized stop, as the nine-month original-source pilot already showed. V3 protected hold continuation stays OFF.

**Interpretation:** The v3 in-sample loss is $2.02 less than the immediately preceding 274-trade control, but the difference is not statistically demonstrated and trades are not paired. Neither profitability nor the owner's original R9 volume target (303,934 trades over Jan–Sep) is met. The four aggressive loosening/sign-inversion diagnostic variants likewise lose money. It is misleading to promote V3 as better because it loses less gross cash while taking fewer trades; both frequency and expectancy gates FAIL.

Pre-existing Micro180 full Jan–Sep pilot (no governor) used all **72,129,347 source quote rows**, obtained **61,258** trades, **-$24,158.30** modeled net, all nine months losing, while original R9 frozen control was **303,934 trades, -$120,212.46**. That pilot used seven-day warmup partitions, so not whole-chain MT5 parity.

The v3 port in `asymmetric_v3.py` overlays the already integrated Python research engine and utilizes quote-derived M1 EMA20/Wilder DI14 with quote-only proxy fallback. The separate MQL5 fork already uses `iADXWilder`, M1 `iMA`, M1/M5 `iATR`, and `CopyTicks` millisecond catch-up. **Exact native MQL5 parity of the new V3 formula is NOT implemented, compiled or verified**, so V3 trading must remain OFF on terminals. Neither old 155-feature AUC nor reconstructed tick libraries were used.

## Boundaries for any next adjustment
- Always test *BUY and SELL separately*, across session and spread regimes, with original no-lookahead quote order. No endless threshold sweeps on previously inspected Jan–Sep.
- Simultaneous full-system acceptance: completed trades >= 303,934 over same nine months **and** net account cash >0 after verified costs **and** smaller economic tail risk, plus broker/account exposure constraints. If any fails, research FAIL rather than changing labels.
- The governor must be enabled for the **deployment-comparable** run; economic no-governor comparators are explicitly non-deployable.
- To genuinely improve expectancy, first study per-signal **MFE/MAE/first-passage and quote excursion** conditional on entry-side, spread, 180s run-up and signal cadence. Indicator weighting alone is not proven.
- Later untouched out-of-sample source is mandatory before a production EA decision. No original MQ5 changes, market data rewrites, or raw file uploads.
