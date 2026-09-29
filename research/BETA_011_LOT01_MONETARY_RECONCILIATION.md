# BETA 011 — Full Jan–Jul XAUUSD 0.01-lot Monetary Audit

**Status:** Replayed all seven monthly original Dukascopy compressed tick files against the frozen BETA 010 trade engine; no R9 hold/exit rewrite, no MQL5 code, no August, no promotion. Current owner review paused for monetary/broker-spec clarification.

## Calculation contract

For USD-quoted spot XAUUSD using a **100-troy-ounce contract per 1.00 standard lot**, the assumed 0.01-lot position is **one ounce**. Cash gross result of one trade is `(exit bid − entry ask) × 100 × 0.01` for a BUY and `(entry bid − exit ask) × 100 × 0.01` for a SELL. Net result = gross cash price movement − roundtrip commission for that 0.01-lot trade. Spread is automatically represented because the simulator enters at Ask and sells at Bid or vice versa. Conversion multiplier = `100 × 0.01 = 1 USD / 1 USD-per-ounce movement`.

The old simulator expressed `net = side-adjusted exit-entry XAUUSD price distance − 0.20` without explicit contract/lot variables. **Under the standard 100-oz contract and 0.01 lot assumption, the old numeric dollars are already correctly scaled.** The old **$0.20 fee per 0.01-lot trade is an assumption, not a measured Coinexx commission.** It would correspond to $20/standard-lot roundturn; a $7/lot roundturn would be $0.07 per 0.01-lot trade. Both are evaluated below without endorsing either fee as the actual broker tariff.

## Independent raw-tick replay and checks

The new auditor programmatically instruments the frozen simulator to return each completed trade’s **pre-fee signed gold price movement**, validates exact match against the legacy $0.20 net, gross profit, gross loss and realized-balance drawdown **for each month independently**, then revalues the same trade path under $0.00, $0.07, $0.20 and $0.40 roundtrip fees. All seven monthly compare-to-original assertions passed. Original source hashes and gzip CRC were checked by the monthly source loader. **57,527,562 original quotes** total; no synthetic bars for fills. `BETA_011_LOT01_CASH_PNL_AUDIT.py` and monthwise atomic JSON checkpoints are the reproducibility record.

## Fee = $0.20 per 0.01-lot trade — original modeled economic amounts

| Month | Trades | Winning trades | Net USD | Gross profit USD | Gross loss USD | Month-local realized DD USD |
|---|---:|---:|---:|---:|---:|---:|
| 2026-01 | 31,250 | 4,189 | -26,651.53 | 1,329.89 | -27,981.41 | 26,651.53 |
| 2026-02 | 27,117 | 4,350 | -26,369.97 | 1,893.36 | -28,263.33 | 26,369.97 |
| 2026-03 | 49,444 | 7,938 | -46,486.59 | 3,042.64 | -49,529.22 | 46,486.59 |
| 2026-04 | 30,134 | 4,064 | -26,622.60 | 1,243.85 | -27,866.45 | 26,622.60 |
| 2026-05 | 31,178 | 4,138 | -24,605.62 | 1,073.52 | -25,679.14 | 24,605.62 |
| 2026-06 | 34,522 | 4,662 | -27,614.39 | 1,212.95 | -28,827.34 | 27,614.39 |
| 2026-07 | 23,051 | 2,363 | -19,670.94 | 575.84 | -20,246.77 | 19,670.94 |
| **Jan–Jul total** | **226,696** | **31,704** | **-198,021.63** | **10,372.04** | **-208,393.67** | **198,021.63** |

The month-local realized DD figures at $0.20 equal the magnitude of each month’s loss for this trial; the global seven-month DD was computed with a continuous realized-balance peak/trough across monthly ledgers, **not the sum of monthly peak-to-trough drawdowns**. These are closed-trade balance drawdowns, NOT tick-by-tick mark-to-market equity drawdowns. The simulator does not model margin calls or prevent negative balance.

## Full seven-month fee sensitivity — same positions, same 0.01 lot, 100 oz/lot

| Roundtrip fee per 0.01-lot trade | R9-like control net | Adaptive candidate net | Candidate gross loss | Candidate realized DD | Candidate winners | Absolute winner-count gain | Relative win-rate gain | Net-loss reduction |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $0.00 | -186,885.04 | -152,682.43 | -172,709.37 | 152,682.43 | 63,064 | +5.79% | +14.98% | 18.30% |
| $0.07 | -204,133.32 | -168,551.15 | -184,392.37 | 168,551.15 | 54,412 | +6.80% | +16.09% | 17.43% |
| $0.20 | -236,165.84 | -198,021.63 | -208,393.67 | 198,021.63 | 31,704 | +10.13% | +19.70% | 16.15% |
| $0.40 | -285,446.64 | -243,360.83 | -249,226.10 | 243,360.83 | 15,441 | +14.43% | +24.38% | 14.74% |

**Important interpretation:** The BETA 010 **+10.13% more winning trades** statement is valid ONLY under the assumed $0.20 fee. At $0.07 fee, winning-trade count gain is just **+6.80%**, although relative win-rate improvement **+16.09%** and net-loss reduction **17.43%** remain. Therefore, the absolute winner-count >10% subclaim is fee-dependent and must NOT be presented as broker-certified or universal. At $0.00 fee the candidate is STILL losing $152,682.43; removing the commission alone does not change its negative economics. The prior 16.15% net-loss reduction under $0.20 is real as a same-feed backtest comparator, but neither candidate nor baseline is profitable.

## What remains unverified / decision implications

1. **Actual Coinexx XAUUSD contract size and fee schedule** are not proven by the Dukascopy feed or prior Python program. The reference 100 oz/lot is common and is consistent with the original `InpLots=0.01` MQL5 default, but terminal `SYMBOL_TRADE_CONTRACT_SIZE`, `SYMBOL_TRADE_TICK_VALUE` / `SYMBOL_TRADE_TICK_SIZE` and actual commission need confirmation on the owner’s Coinexx MT5. Account currency assumed USD. In MQL5 the authoritative broker conversion can be checked with `OrderCalcProfit(ORDER_TYPE_BUY, "XAUUSD", 0.01, 3000.00, 3001.00, profit)` and the contract/tick properties. An exact $1.00 gross result would confirm the assumed USD-per-oz scaling; if it differs, rerun cash reconciliation with the actual factor.
2. The original PnL label `net profit` represents an UNCONSTRAINED cumulative research sum. It is NOT profit achievable on any specified $100, $200, $500, or $100k deposit. The cash-equity path breaches zero with those deposits, and the research model has no margin, stop-out, slippage, latency, swap, rejected orders or account-constrained sizing. Declared drawdown equals peak-to-trough from **realized closed trades only**; it is not the MT5 tick-marked max drawdown. These limitations are material, not notation.
3. `gross_profit` / `gross_loss` in this research simulator are grouped **AFTER subtracting the modeled commission from each closed trade**. Other tester/report conventions may list gross trading PnL and commission separately. Do not compare the labels without normalizing the conventions.
4. BETA 010 was tuned after January exploratory screening. Jan–Jul data are repeatedly researched and thus NOT pristine out-of-sample; a genuine forward validation or broker real-tick test is still necessary. No approved MQL5 EA exists.
5. Preserve R09_BETA_001 as a positive **entry-accuracy diagnostic candidate**, but hold any unqualified broker-equivalent $-P&L claims pending contract/cost/margin reconciliation and owner approval. Do NOT dismiss the entry concept based on an imagined missing lot multiplier; likewise do NOT describe this negative outcome as profitable.

## Source material

- Read-only original R9 MQL5 input `InpLots=0.01`: `https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/r9-tick-logger/Experts/GoldMuwahahaMiner_R9_TickLogger.mq5`.
- Frozen BETA009 simulator and BETA010 experiment scripts under the repository independent `beta` research branch. No strategy-condition changes made in this monetary audit.
- Official MQL5 CFD cash formula: `https://www.mql5.com/en/book/automation/experts/experts_ordercalcprofit`.
- Broker terminal property documentation: `https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants`.
- Broker-specific final profit value function: `https://www.mql5.com/en/docs/trading/ordercalcprofit`.
- Previous BETA 010 white paper: `https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/beta/research/whitepapers/R09_BETA_001_ADAPTIVE_IGNITION_ENTRY.md`.
