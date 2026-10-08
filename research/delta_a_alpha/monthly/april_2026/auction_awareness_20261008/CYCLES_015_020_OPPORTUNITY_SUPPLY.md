# Delta-A-Alpha — April Weakness and Opportunity Supply Research 015–020

**Status:** EXPERIMENT COMPLETE; OPPORTUNITY-AWARENESS CANDIDATE ONLY; NO V1/EA PROMOTION. Owner May 137 paused. August sealed. April 136 original checkpoints unchanged.

## Durable exact-byte research

In the user's project Library:

`/xauusd-trading-bot/delta-A-alpha/monthly/april_2026/vertical-grid-136/auction-awareness-20261008/weakness-opportunity-supply-015-020/`

- `DAA_APRIL_WEAKNESS_OPPORTUNITY_SUPPLY_RESEARCH_015_020.md` — full methodology, failure modes, separate test phases, constraints, code contracts, external research.
- `DAA_APRIL_OPPORTUNITY_SUPPLY_CYCLES_015_020_20261008.tar.gz` — seven exact Python scripts, atomic JSON checkpoints for all cycles, study, checksums. Archive SHA256 `10ca26418230a01a98b4a6a796734e3e0bef512550d58f6f5a11dad21f608e9d`.
- `SHA256SUMS_015_020.txt`; `OPPORTUNITY_TAIL_ABLATION_CYCLE_018.json`; `FUNDED_RENEWAL_CAPITAL_AUCTION_CYCLE_020.json`; `HTF_NATIVE_CYCLE_016_PRIOR_SELECTION.json`.

## Diagnosis

Actual Jan/Feb/Mar/Apr Dukascopy XAUUSD completed M5 median high-low $4.883/$6.970/$7.570/$5.025. Bars with >=$10 range 17.67%/31.40%/32.91%/11.73%; >=$20 range 5.87%/9.26%/6.89%/1.36%. April's *profitable-excursion supply* dried up relative to March, but one-hour path efficiency hardly changed. January central volatility resembles April: no calendar or one-feature April detector is defensible. Raw April sampled median spread $0.710, normalized April-136 assumed $0.20; market friction matters critically.

## Honest sequential experimental outcomes

- **015:** Full Jan–Apr time-series diagnostic using actual completed M5 and sampled raw quote spread.
- **016:** Five original causal H4/H1/M15/M5 signal families × four original raw Bid/Ask first-touch exit policies × two strict physical caps. Jan–Feb development with March validation, 0/40 meet minimum profitability, PF, velocity gates. April diagnostics only, no cherry-picking.
- **017:** JanFeb-trained opportunity-supply forecast (predict next 1h with ≥2 M5 bars spanning ≥$10), March validation, April out-of-sample labels; signal does NOT predict direction or profits.
- **018:** Simpler 8-feature past completed M5 range/tail logistic AUC **0.8500 March** / **0.8045 April** (412 approximately hourly nonoverlapping April examples), Apr Brier skill **+0.2951** vs JanFeb-constant, blocked approximate 95% AUC **0.736–0.853**. Bottom/highest predicted April quintiles: **6.0% vs 68.7%** realized opportunity. Extra H4/POC/spread features decreased April AUC to **0.7838**. Thus a predictive market-*character* discovery, **not trading alpha**.
- **019:** Retained-exit April event-ledger raw-quote repricing with JanFeb-trained forecast. April-selected original signals and old exits mean **not independent raw first-touch trading**. Tested .35/.50/.65 gates after seeing April; all threshold choices contaminated for blind-strategy claims.
- **020:** Strict one ticket per *unique timestamp tick*, physical funding requires prior funded exit/fast-win proof, global cross-layer cap, actual full-tick Bid/Ask floating-equity reconstruction of *retained original entry/exit timestamp portfolios*. At cap128 core+renewal baseline **+$34,499.19 / 10,130 tickets / -$4,045.48 gross loss / PF9.528 / equity DD $1,813.05** versus forecast p≥.5, observed spread≤$0.75 gate **+$36,044.45 / 6,639 tickets / -$2,378.95 gross loss / PF16.151 / equity DD $1,608.92**. It improves $1,545 net but sharply cuts velocity. Cap4: $2,672.50→$2,732.37, cap16: $10,386.60→$10,569.63. Each simulated lot .01. All exit P/L reconstruction differences at source precision zero. **This is archived April-selected retained-exit sensitivity, NOT a new raw-first-touch EA backtest.** MT5 slippage, Coinexx parity, true original order path, margin, small-balance survivability unproven.

## Causal proposed interface

L0 ordered BidAsk/quote root → L1 keep Asia and London/overlap/NY distinct session geometry → L2 completed H4/H1/M15/M5 price structure PLUS independently validated **Opportunity Supply** estimate using past 12/48/144 completed M5 ranges → L3 HIGHVOL and L4 ASIA generators still own independent signal cadence → L5 Watchdog renewal must use completed *funded* prior child and posterior excursion supply/fee coverage → L6 native continuation only after independent structural qualification (40 simple attempted new entries FAILED) → L7 bounded conditional wrong-direction recovery → L8 final physical capacity/actual floating equity/margin stop. Month/date/hour cannot be a new switch. No Martingale, no loss dependent lot, no hidden model, one ticket per tick absent named scaling authorization.

Candidate trigger p>=0.50 + spread <=$0.75 **is research-only**, since April saw threshold comparison; a truly blind deployment strategy needs prior-only selection of admission and exit rules + genuine raw-quote first-touch regeneration then independent unseen testing. May remains paused until owner authorization. R9 SYNTH and January–March research frontiers remain benchmarks, not execution oracles.

## Reconstructible community context
- MQL5 tick-count (not exchange trade volume) profile https://www.mql5.com/en/articles/23169
- Chinese/Japanese MarketProfile/TPO https://www.mql5.com/zh/articles/16461 , https://www.mql5.com/ja/articles/16461
- transparent Bayesian online change-point https://www.mql5.com/en/articles/23482
- no true market depth: academic OFI is not reconstructible from quote-only files https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1712822
- portfolio margin principles https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/buying-power

**No merge, no scientific cursor change, no May consumption, no sealed August access.**