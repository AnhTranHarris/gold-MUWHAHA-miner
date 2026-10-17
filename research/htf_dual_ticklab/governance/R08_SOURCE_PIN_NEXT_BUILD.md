# XAUUSD HTF — R08 Causal First-Passage & Online Specialist Evidence

**Classification:** RESEARCH ONLY — NOT INVESTOR CERTIFIED, NOT LIVE / DEMO DEPLOYED.
**Reference branch:** `carson/htf-time-matured-opportunity-r08`; direct ancestor R07 `aaaa191f15f6386f02cfb8e690cd42f390cd94c9`.

## Exact complete Drive research source
MT5_EXPAND / 04_EXPERIMENT_RESULTS_AND_VALIDATION:  
https://drive.google.com/file/d/1lzjIFjCl-IHI3x7LZG3OcexyP3qV50Cn/view

- **ZIP SHA-256:** `52e66ad2c0c0aa69b6118176189b1cdbb1a611029d1dbd050843b42f6f17384b`
- **Size:** 3,678,845 bytes; **60 members** and CRC integrity verified after cloud readback.
- Contents: 6 native-broker research Python scripts; causal signal feature construction; first-passage/price-cost/online shadow research models; frozen January training; February validation; trade ledgers; per-source fingerprints; full human-readable findings and next-build specification. The original raw tick sources remain in PRIMARY Drive. The ZIP intentionally excludes duplicating original source tick arrays.
- The independent research scripts in Drive are **not yet GitHub-source-parity integrated** into official `Replay`. This GitHub branch adds the *tested* general-purpose mature-evidence book only. Do not claim tick-for-tick parity, complete investor S/S' qualification, or actual live profitability from CI.

## Exactly authorized four original monthly inputs
- Coinexx January SHA-256 `1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`, UTC source minus 120min.
- Coinexx February SHA-256 `5de772aab4d15ebf18aa48850e847c98e2bcb639064790bbed9d87a598c3bf05`, UTC source minus 120min.
- Dukascopy January SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5d`, native UTC.
- Dukascopy February SHA-256 `ed3b3545c990c88d78519594c17c8915b0f679adcb0a94920ba7524f1f6d5c5d`, native UTC.

R08 selected **Jan 5–8** and **Feb 3–6** UTC windows: **7,130,876 actual original ticks** (not the complete source months). The source ZIP report names all experiment sizes and research caveats. All four original whole-file compressed SHA-256 identities were rechecked.

## System advancement
1. Per-broker cost-corridor measurements (Coinexx median $0.19/$0.21 price spreads vs Dukascopy $0.696/$1.043 across sampled January/February observed seconds).
2. Causal S1 features combining RSI, Fibonacci, ATR-compatible volatility context, anchored quote-weighted reference, M5/H1 contextual proxies and bid/ask costs.
3. Triple-barrier original-tick entry/stop/target/time outcomes, six profile×side first-passage predictors, trained Jan and frozen for Feb.
4. Chronological online 30-arm proposal allocator: previous trade/shadow rewards mature only after exit; P&L cannot be credited to cash at entry.
5. Independent session-by-volatility routing diagnostics and **1,080** dynamic broker-cost-normalized event screens; neither should be called funded full-account proof.
6. New tested `htf_ticklab/matured_opportunity.py` with `tests/test_matured_opportunity.py`: never use future outcomes before maturity, preserve broker identity, reject stale/backfill, quarantine unobserved specialists.

## Explicit outcome and next action
No January-fitted R08 system demonstrated *both* high throughput and positive net on both independent brokers in the February checks; absence of transferability is not evidence that every possible EA must fail. No no-trade, low-trade or non-depletion result is promoted. Investor numerical caps remain TBD.

**R09 exact next build:** implement a rapidly reusable **causal event-token handoff system** combining conditional spread compression, tick-flow acceleration, structural Fib/QWAP acceptance, RSI/ATR phase shifts, broker-specific price improvement and economic stops; integrate as shared-account S/S' controls in the official Python Replay. Full 12-slot broker×$100/$200×0/250/1000ms; continuous month accounting, tick-level equity, all material rejections, and predeclared source-hash verification. Every new candidate needs a separately pinned experiment ID. No MQL5 deployment or live trades.
