# XAUUSD HTF — Jan 2026 Fib/ATR/RSI/QWAP Arm Ablation (UNPROMOTED)

**Study ID:** XAU-HTF-20261016-JAN96-FIB-ATR-RSI-QWAP  
**Decision:** NEGATIVE_RESEARCH_ONLY; no strategy promotion.  
**Archive:** https://drive.google.com/file/d/1FxnbG7bjesCxJDSRkkFSvQ7XdkF1ue0y/view  
**Archive SHA-256:** `ca28439f2c29361514d3edcf0af1a5f159f55e3593f96bfde9c42773aeeab1d8` (531,680 bytes). Exact uploaded bytes were fetched back, hashed, and ZIP CRC validated. Contains full-method Markdown, source/hash manifest, source Python, parameters, 96 trade ledgers, 7,175 hour/day/week/month period rows, decision and integrity receipts. The original authorized tick tapes remain in their PRIMARY Drive source folders and are not copied into the zip.

## Origin, scope and authority
Continues the verified XAUUSD HTF branch `carson/htf-handoff-emergency-v1.3` at `f9ca199d5c7627678b725c915e4c6eab279029da`. Current isolated engineering descendant is `carson/htf-shared-signal-arbiter-v0.1`, with additive `htf_ticklab/signal_bus.py` and tests only. The user expressly authorized community **idea research** in this task (TradingView, ForexFactory, Myfxbook, quant and Reddit). This does **not** authorize external quote data, imported opaque strategies or cross-project branches. Original R9 SYNTH Report 4 is hypothesis context, not an execution benchmark substitute.

**Original market inputs:**  
- Coinexx XAUUSD Jan 2026: 7,699,274 ticks; SHA-256 `1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`; `time_msc` minus 120 minutes as calibrated.  
- Dukascopy XAUUSD Jan 2026: 9,135,062 ticks; SHA-256 `d2ebb9a8c19caad02c5d95d7c6504868722c286e1187d1dbad18098d8c5ec5c5`; native UTC.  
Both compressed source SHA-256 fingerprints freshly computed from original bytes in this research turn.

## Mechanism arms and model limits
`A`: H1 completed rolling swing Fibonacci retracement + H1 directional RSI/EMA + M5 confirmation + M1 RSI cross and QWAP-confluence.  
`B`: H1-neutral RSI, M1 RSI exhaustion-turn and QWAP deviation normalized by completed M5 ATR.  
`C`: H1/M5 momentum-confirmed M1 range breakout and quote-event weighted session price reference.  
Compositions `S` no trade, `A,B,C,AB,AC,BC,ABC`. QWAP means observed-quote weighted mid, **not consolidated trade-volume VWAP**.

Exploratory source-code implementation is in the exact archive, separate from the GitHub production replay. 8 arms × Coinexx/Dukascopy × $100/$200 × 0/250/1000ms = **96** scenarios. Each arm separately shares its own single modeled account, position capacity, equity and margin; no summation of independent stand-alone strategy profits. Fixed assumed 0.01 lot, 100oz/lot, leverage 500, commission $3.50 per lot/side, adverse slippage 0.10 USD/oz each fill, spread ceiling 2.00, modeled stop-distance = max(1.0, 0.6 × M5 ATR), target-distance = max(1.5, 1.2 × M5 ATR), 30min max hold, estimated stop loss capped at an exploratory **5% equity** (NOT investor-approved).

## Evidence — $100, 250ms
| Arm | Coinexx net USD | Dukascopy net USD |
|---|---:|---:|
| S (no trade) | 0.00 | 0.00 |
| A | -26.470 | -23.810 |
| B | -44.740 | -61.611 |
| C | -53.770 | -66.223 |
| AB | -42.420 | -56.871 |
| AC | -61.990 | -65.819 |
| BC | -58.170 | -65.902 |
| ABC | -57.510 | -67.362 |

All **84 active-arm** cases were negative across both starting-capital sizes and all three latencies. No modeled margin stopout was recorded; do **not** mistake this for investor-compliant survivability. ABC $100 Coinexx: 185 trades, after-cost PF 0.8219, maximum marked equity drawdown $83.23; Dukascopy: 89 trades, PF 0.6277, marked DD $92.291. ABC $200 ending balances fell to $42.41 and $32.729 respectively. The historical $100/$200 survival-first mandate was not satisfied.

A pure-Python January Coinexx ABC replay and a separate Numba-accelerated engine reproduced the $100/$200 closed-trade counts, P&L and marked max drawdowns to floating precision. This checks computational consistency, not real venue fills. No unreported favorable scenario, true VWAP, production MT5 trade execution, official investor risk limits, unexamined prospective 2026 holdout or complete mark-to-market equity series was established.

## Constructive next build — proposed, NOT STARTED
Preserve A as a contextual feature candidate only. Next design must move entry timing to causally constructed S5/S15 quote microstructure and use H1 as market context, M5 ATR as cost/volatility normalization, and RSI/QWAP/Fibonacci as conditional evidence rather than a global four-indicator AND gate. Research execution-sensitive state transitions, rejection filters and stop management. Baseline and candidate must use one shared-account arbiter; replay broker feeds independently on matched corrected UTC, all 12 broker/balance/latency slots, preserve losing intervals and falsifiers. Formal candidate experiment needs frozen plan/manifest and investor-approved risk thresholds; the exposed Jan–Sep tape is not an untouched holdout.

## Preservation, defects, rollback
The current code branch adds an independent signal arbiter but does not yet wire it into the CLI or claim multi-position account support; still research-only. The previous enhanced v1.2 QC cloud zip remains unavailable and is a **separate** archive recovery gap. Never replace historical QC bytes with this case or silently release code. Rollback to the verified v1.3 HEAD above. Current result archive is authoritative only as this exploratory **negative** case.
