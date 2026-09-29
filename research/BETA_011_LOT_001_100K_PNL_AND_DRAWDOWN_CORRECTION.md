> **SUPERSEDED FEE ASSUMPTION / READ UPDATED BETA 011 AND BETA 012 FIRST.** This early $0.20 per 0.01-lot research scenario was written before the historical R9 Coinexx deal ledger's $0.01-per-side commission was reconciled. The archive arithmetic and zero-capital pathology are still meaningful *only under that old assumed fee*. Corrected Jan–Jul unlimited-credit P&L/winners use **$0.02 roundtrip** in [the verified fee revaluation](BETA_011_LOT001_PNL_ACCOUNTING_CORRECTION.md); the updated explicitly funded replay is [BETA 012](BETA_012_FUNDED_001LOT_FEE002_REAL_TICK_RECHECK.md). This older report MUST NOT be cited as the final commission-normalized result.

# BETA 011 — 0.01-lot / $100,000 accounting audit of R09_BETA_001

**Scope:** audit and correct interpretation of the previously published BETA 010 P&L, gross loss, and maximum drawdown. **No owner authorization of MQL5 and no approval of a BETA cumulative baseline.** Full January–July original Dukascopy execution from the archived research is preserved as a **counterfactual unlimited-credit sequence**, not a funded Coinexx Strategy Tester outcome. August sealed.

## Finding — the existing USD calculations are conditional, but the $100k-account outcome was mislabeled

The archived source `BETA_009_JAN_JUL_ENTRY_CANDIDATE_VALIDATION.py` has **no explicit lots, SYMBOL_TRADE_CONTRACT_SIZE, starting deposit, free margin, margin call, stop-out, broker tick value or broker commission table**. It computes (buy `bid_exit − ask_entry`, sell `bid_entry − ask_exit`) as a raw XAUUSD USD/oz price difference **minus a flat assumed $0.20 per completed trade**. If the gold contract is 100 troy oz per 1.00 lot and account is USD, 0.01 lot represents **one oz**, so raw $/oz delta happens to equal USD P&L for 0.01 lot. This is **implicit** rather than verified by the source code, and Coinexx's exact live symbol settings and commissions were not read from MT5.

MQL5's CFD/Forex profit convention is `(close_price - open_price) × SYMBOL_TRADE_CONTRACT_SIZE × lots` for a long (negative for short); `OrderCalcProfit()` is the source of broker-currency estimates. Coinexx-affiliated commodity description says 1 gold lot represents 100 oz, but the owner's terminal `SYMBOL_TRADE_CONTRACT_SIZE`, `SYMBOL_TRADE_CALC_MODE`, `SYMBOL_TRADE_TICK_VALUE`, `SYMBOL_TRADE_TICK_SIZE`, currency, stop level, commission, leverage and stop-out must be captured before certifying broker parity. No re-scaling by **0.01 a second time** is allowed when $/oz is already a $/trade amount at 1 oz exposure.

**Crucial failure:** the simulator starts the P&L accumulator at 0, never adds $100,000 to the trading feasibility check, never checks margin or stop-out, and reports `peak - cumulative_realized_PnL` as “equity” drawdown even though floating P&L during open positions is excluded. Thus the archival `−$198,021.63` net and `+$198,021.63` maximum realized balance drawdown represent what **226,696 trades on unlimited synthetic credit** would have produced, and **cannot** be a faithful account result with $100,000 initial funds. The R9 same-feed control also **removed the original Coinexx `_Point`-based 25-point entry spread gate**, further preventing direct comparison to historic Coinexx R9 REAL.

## Independent decimal arithmetic audit of the archived unlimited-credit series

| 2026 UTC month | Net P&L (USD) | Gross profit (USD) | Gross loss (USD) | Hypothetical closing balance with unlimited trading after zero, starting $100k |
|---|---:|---:|---:|---:|
| Jan | −26,651.53 | +1,329.89 | −27,981.41 | $73,348.47 |
| Feb | −26,369.97 | +1,893.36 | −28,263.33 | $46,978.51 |
| Mar | −46,486.59 | +3,042.64 | −49,529.22 | $491.92 |
| Apr | −26,622.60 | +1,243.85 | −27,866.45 | **−$26,130.68 — impossible as continuously funded test** |
| May | −24,605.62 | +1,073.52 | −25,679.14 | −$50,736.30 |
| Jun | −27,614.39 | +1,212.95 | −28,827.34 | −$78,350.69 |
| Jul | −19,670.94 | +575.84 | −20,246.77 | −$98,021.63 |
| **Archive total** | **−198,021.63** | **+10,372.04** | **−208,393.67** | **−$98,021.63** |

These totals reconcile directly (full precision before rounding). The archive's reported max drawdown is **$198,021.63**, or **198.02%** of the stated $100k deposit; it is *not* a viable account equity drawdown. It is a peak-to-trough statistic on an uncapped realized trade-result accumulator. It is also not a measured mark-to-market equity DD.

## Independent capital-aware replay for a controlled illustration (NOT Coinexx certification)

A new independent direct-tick replay (`BETA_011_CAPITAL_AWARE_TICK_REPLAY.py`) explicitly uses `lots=0.01`, assumed `contract_size=100 oz/lot`, `initial_deposit=$100,000`, actual original Dukascopy Bid/Ask and original frozen Hold/Exit, $0.20 per completed trade, single position, and models **two illustrative margin terms**:
- 100:1 leverage, stop-out at 50% margin level;
- 500:1 leverage, stop-out at 50% margin level.

The replay checks margin before entry and floating equity vs a stop-out margin threshold on every tick; it permanently stops on the first signal for which the account cannot supply required margin (rather than pretending the owner would continue trading after funds are depleted). These leverage/stop-out values are **hypothetical**, not read from Coinexx account settings. Both original historical R9 and candidate were run with matching accounting rules.

| Illustration, original $100k deposit | Same-feed R9 control | R09_BETA_001 candidate |
|---|---:|---:|
| **100:1**: trades before insufficient margin | 94,002 | 108,230 |
| **100:1**: wins | 11,794 | 16,540 |
| **100:1**: net | −$99,951.93 | −$99,953.38 |
| **100:1**: gross profit | +$4,392.00 | +$6,286.10 |
| **100:1**: gross loss | −$104,343.93 | −$106,239.48 |
| **100:1**: realized balance DD | $99,951.93 | $99,953.38 |
| **100:1**: remaining balance | $48.07 | $46.62 |
| **100:1**: first insufficient-margin entry attempt (UTC) | March 18, 15:26:59 | April 1, 05:49:51 |
| **500:1**: remaining balance | $9.85 | $9.22 |
| **500:1**: first insufficient-margin entry attempt (UTC) | March 18, 15:53:25 | April 1, 06:09:14 |

These replays validate the archive's **Jan–Mar** 0.01-lot-one-ounce price P&L convention for the candidate before the funding issue and identify the approximate time when 100:1 or 500:1 funded trading ceases. May–July were intentionally **not replayed under already-stopped scenarios**; there is no remaining funded equity to continue trading. The capital-aware numbers above are **not** Coinexx's exact gross-profit/loss or MT5 equity-DD report and do **not** prove survival, owner approval, or an economically profitable strategy. Because both variants eventually lose nearly the funded deposit, the historic unlimited-credit loss-reduction percentage cannot be used to promote the candidate as a funded-account winner.

## Further normalization required before an EA promotion decision

1. Obtain authoritative broker symbol settings on the owner's Coinexx MT5 connection (one compact `SymbolInfo*` report), account currency, leverage, netting/hedging, spread units, tick value, tick size, stops, commission and stopout. Avoid inventing real Coinexx conditions from generalized broker advertisements.
2. Model 0.01 lots explicitly (contract volume 100 oz × .01 = 1 oz if confirmed) and use actual commission per side/roundtrip; do not blindly keep $0.20. In a 226,696-trade archive a $0.20/trade assumption contributes **$45,339.20** by itself. Gross-profit/loss classification must be recalculated per trade if commission changes; aggregates cannot simply be relabeled.
3. Reproduce original R9's point-based maximum-spread entry filter faithfully and, separately, assess source-feed spread sensitivity. January original Dukascopy full-source recorded mean Bid/Ask spread ≈ **$0.8414/oz**, which is much larger than the $0.30/oz stop parameter; spread-to-stop economics are decisive. Source feed differences prevent a direct comparison with historic Coinexx `R9 REAL −$50,285.28`.
4. Calculate proper funded mark-to-market **equity DD**, realized balance DD, margin-level dynamics, rejection due stop distances, slippage and account stop-out as separate fields. Do not allow entry at insufficient balance or margin. Reconcile per-trade completed fills to a broker contract reference, not merely arithmetic sum.
5. Re-run the SAME-FEED funded R9 vs adaptive entry with corrected economics; if any January candidate produces a **preregistered valid >10% economic/entry improvement without an unacceptable loss of solvency**, extend Jan–Jul and reconfirm the owner gate. The original entry signals/logic stay archived as a research idea, but its prior **formal-qualification/economic-statistics claims are ON HOLD**, not erased or silently accepted. No MQL5 coding before explicit owner approval.

## Evidence provenance and original code boundary

- Existing immutable scorecard: `R09_BETA_001_ADAPTIVE_IGNITION_ENTRY_SCORECARD.json`.
- Existing simulator: `BETA_009_JAN_JUL_ENTRY_CANDIDATE_VALIDATION.py`; primary monthly script: `BETA_010_PRIMARY_MONTHLY_METRICS.py`.
- BETA 011 reproducible decimal/math audit: `BETA_011_PNL_LOT_MARGIN_ACCOUNTING_AUDIT.py` + JSON.
- BETA 011 new scenario direct-tick funded replay: `BETA_011_CAPITAL_AWARE_TICK_REPLAY.py` + JSON.
- MT5 official formulas: https://www.mql5.com/en/book/automation/experts/experts_ordercalcprofit and https://www.mql5.com/en/docs/trading/ordercalcprofit; strategy test equity/stop-out: https://www.metatrader5.com/en/releasenotes/terminal/2125; Coinexx gold contract example: https://coinexxltd.com/commodities/.
- This is a corrective research checkpoint. Neither the source R9 EA nor `R09_BETA_001` candidate was changed or ported to MQL5. August remains SEALED.
