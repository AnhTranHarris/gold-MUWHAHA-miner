# BETA 012 — Corrected Coinexx R9 deal-fee / 0.01-lot / $100k funded-tick feasibility check

**Evidence priority:** This document supplements (does not replace) `research/BETA_011_LOT001_PNL_ACCOUNTING_CORRECTION.md` and its verified Jan–Jul 0.01-lot `0.02`-fee scorecard. Any prior BETA011 note still describing $0.20 as the best available fee assumption is *superseded* by the matched historical Coinexx R9 ledger's observed **$0.01 each entry/exit deal**, or **$0.02/0.01-lot roundtrip** (as recorded in BETA011). Costs may differ for another Coinexx account, period, or symbol; confirm terminal deal commission on future MT5 runs.

## Corrected P&L formula and what failed

For one position at 0.01 lot with verified/reported gold contract convention of 100 troy ounces/lot, the effective exposure is one ounce. The financial calculation from the source is the signed exit-entry price difference in USD/oz multiplied by `0.01 × 100 = 1`, then **deduct $0.02**, not the obsolete $0.20 fee. The earlier source's lot *price* multiplier was correct **implicitly**; the commission was inflated 10x. Corrected full Jan–Jul same-feed, unlimited-credit research series from BETA011 is:

- candidate: **226,696** trades, **61,650** wins (**27.20%**), net **−$157,216.35**, gross profit **+$18,776.18**, gross loss **−$175,992.53**, realized-balance peak-to-trough **$157,216.35**.
- R9 feed-normalized control: **246,404** trades, **58,279** wins (**23.65%**), net **−$191,813.12**, gross profit **+$16,701.11**, gross loss **−$208,514.22**, realized balance DD **$191,813.12**.
- candidate win count gain **+5.78%**, relative win rate **+14.98%**, net-loss reduction **18.04%**. The earlier **+10.13% win-count improvement** was an artifact of the $0.20 assumed fee and must not be promoted as the actual Coinexx-linked result.

**But:** neither simulator checks actual Coinexx account margin/stopout or floating-equity drawdown. The `−$157,216.35` and `−$191,813.12` are unlimited-credit counterfactual sums, NOT results possible from a $100,000 funded MT5 account running all seven months with no deposit.

## New explicitly funded, original-tick 0.01-lot scenarios

The owner requested re-audit for a $100k initial account and 0.01 lots. The new `BETA_011_CAPITAL_AWARE_TICK_REPLAY_FEE002.py` directly reads original Dukascopy Jan–Apr, uses `lots=0.01`, assumed `contract_oz=100`, $100,000 deposit, actual Bid/Ask fills and original fixed R9 Hold/Exit, **$0.02 per completed trade**, and halts on the first entry for which available balance is insufficient to supply notional-based margin. It checks floating P&L against an illustrative 50% margin stopout on every observed tick. The resulting first-ineligible-entry cutoff is shown below (all times UTC). This is NOT exact Coinexx testing: true leverage, stopout, symbol stops/tick values, fees for future trades and execution/slippage need a broker-specific model.

| Illustrative model | R9-like control | Adaptive entry candidate |
|---|---:|---:|
| **100:1 leverage**: trades | 113,492 | 135,633 |
| 100:1: winners | 26,679 | 36,832 |
| 100:1: net P&L | −$99,954.96 | −$99,954.90 |
| 100:1: gross profit (after per-trade fee, positive outcomes) | +$9,230.85 | +$12,591.55 |
| 100:1: gross loss (after per-trade fee, negative outcomes) | −$109,185.81 | −$112,546.45 |
| 100:1: realized balance DD | $99,954.96 | $99,954.90 |
| 100:1: remaining balance | $45.04 | $45.10 |
| 100:1: no margin for next entry | **April 2, 06:15:49 UTC** | **April 29, 14:12:31 UTC** |
| **500:1 leverage**: trades | 113,560 | 135,694 |
| 500:1: net P&L | −$99,991.29 | −$99,991.77 |
| 500:1: remaining balance | $8.71 | $8.23 |
| 500:1: no margin for next entry | **April 2, 07:01:19 UTC** | **April 29, 14:38:53 UTC** |

The 100:1 model uses margin `(entry_price × 100oz × 0.01lots) / 100`; the 500:1 uses denominator 500. Stopout condition is `balance + open_unrealized_PL < .50 × reserved_margin`. These settings are *scenario parameters*, not observed Coinexx account values. The early replayed months precisely replicate the corrected BETA011 cash convention (for candidate Jan net −$21,026.53, Feb −$21,488.91, Mar −$37,586.67). Once every modeled funded account hits an entry-margin boundary in April, May–Jul are marked **NOT TRADABLE / NOT REPLAYED**, not booked as additional funded losses or profits.

## Interpretation and decision rule

1. Correct 0.01-lot scaling is **not** the source of the earlier $198k result if the symbol has 100oz/lot; the excessive commission ($0.20 vs observed $0.02) is one significant discrepancy.
2. The much larger discrepancy against the original historical Coinexx R9 REAL −$50k remains unexplained by lot or commission alone. This feed-normalized Python simulator **disabled the actual R9 `_Point`-based 25-point spread rejection**, while Jan Dukascopy quotes averaged about $0.841/oz spread. The symbol is XAUUSD throughout, but quote feeds, spreads, fills, stop levels, tester account enforcement and order acceptance differ. Do NOT equate Dukascopy and Coinexx test results.
3. All funded scenarios remain economically negative and use near the whole hypothetical starting deposit before trading is blocked. Neither $99.95k realized balance DD nor unlimited-credit $157.2k is an MT5-style marked-to-market **equity** DD; that remains uncomputed.
4. Entry skill remains worth researching: the candidate's win rate, absolute wins and time-to-funding-exhaustion increase versus the comparable same-feed control. But the archived **formal winning-candidate** label, >10% absolute winning-trade claim and any MQL5 coding permission remain **ON HOLD** pending a faithful, funded broker-contract and cost revalidation with explicitly defined owner gate.
5. This report is an audit of the prior fixed entry / hold / exit logic; it does not develop a new trading strategy, use August, or authorize MT5 coding.

## Reproducibility and lineage

- Durable `beta` source record: `research/BETA_011_LOT001_PNL_ACCOUNTING_CORRECTION.md`, with original Coinexx R9 deal price + commission evidence.
- Corrected seven-month per-trade BETA011 monetary audit and source: `research/BETA_011_LOT01_MONETARY_RECONCILIATION.md`.
- New capital-aware replay code and result file: `BETA_011_CAPITAL_AWARE_TICK_REPLAY_FEE002.py`, `BETA_011_CAPITAL_AWARE_TICK_REPLAY_FEE002.json` in BETA_RESEARCH Google Drive.
- Read-only source: `BETA_009_JAN_JUL_ENTRY_CANDIDATE_VALIDATION.py` and original January–April compressed Dukascopy XAUUSD Bid/Ask ticks. August sealed.
