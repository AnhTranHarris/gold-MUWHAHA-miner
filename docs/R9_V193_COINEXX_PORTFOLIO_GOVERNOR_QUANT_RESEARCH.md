# R9 v1.93 Coinexx-only portfolio-gross-loss / indicator research
2026-11-13. **EXPERIMENTAL. DO NOT ATTACH TO FUNDED OR LIVE TRADING UNTIL COMPILE, COMPLETE REAL-TICK REPLAY, AND DEMO ACCEPTANCE.**

## Locked sources and scope
- Exact critical rollback: commit 8729a6345655a7b4ea31facc81982004ee2b8921 / EA blob 7eecb5f1947017a01ce85b2520725de54749e523.
- This branch forks directly from the R9 v1.90 rollback. The v1.90 rollback remains unchanged. It is NOT the v1.92 QRB/QAF enabled shadow integration.
- **Only original Coinexx Bid/Ask TickLogger / broker quote exports are allowed as historical market data.** Dukascopy is neither used nor needed. Do not redownload, regenerate, re-sort, deduplicate or duplicate raw ticks.
- Historical markets provide *no* fill confirmations, broker fees, account equity or margin. R9 v1.93 obtains these in a running MT5 terminal from live account/deal APIs. Research uses explicit non-certified assumptions.
- **No LightGBM model is embedded here.** Previous mean five-second AUC ~0.7385 pooled and ~0.7232 original R9 side was for retrospective fixed first-passage labels, not executable net-trade expectancy. Owner permits research to proceed below preferred 0.75; do not reinterpret these scores as a proven P&L edge.

## Concrete code
- Experts/GoldMuwahahaMiner_R9_HybridGate.mq5 version 1.93 is the isolated new EA.
- Experts/GoldMuwahahaR9PortfolioGovernor.mqh implements all-symbol/all-magic account gross-loss monitoring and order-risk checks.
- Experts/GoldMuwahahaR9M1IndicatorContext.mqh implements M1 completed-bar ADX(14), +DI/-DI, EMA(20), ATR(14), plus completed-second quote impulse for a purely observational decision context. The optional experimental weak-S1 entry rescue is OFF by default.
- Experts/GoldMuwahahaR9CashGeometry.mqh implements broker-profit-conversion scenario math for a net 1.75 account-currency cash objective. The cash-geometry log is OFF by default; it never gates trade entry.

## Portfolio gross-loss governor formulas and monetary units
Let E0 = the first observed equity on this broker calendar day, persisted in terminal global variables; Ep = persistent observed equity peak, both in account currency.

Gross spent from ALL account deals today:
L_realized = sum over market deals max(0, -(DEAL_PROFIT + DEAL_SWAP)).
C_paid = sum max(0, -DEAL_COMMISSION) + sum max(0, -DEAL_FEE) + negative stand-alone commission/charge deals.
L_float = sum over ALL current account positions max(0, -(POSITION_PROFIT + POSITION_SWAP)).
D = L_realized + C_paid + L_float. Winners never directly cancel losses.

Gross cash budget B = min(0.12 E0, 0.04 E0 + 0.25 G_realized), where G_realized is today's sum of positive gross market-deal profit/swap components; configurable inputs. This is a bounded partial profit-funded budget, not an unlimited loss replenishment.

HARD HALT if D >= B, OR equity from observed persistent peak down more than 10%, OR current account margin level below 150% (with positive margin). Halt persists for the broker day via account-login-specific terminal global variables. One may only reset via the new broker day in the current implementation; DO NOT delete risk-global variables to force a trade.

PRE-ENTRY requirement: D + projected cash loss to requested stop + cash reserve <= B; estimated post-order free margin >= 10% of current equity. Uses native OrderCalcProfit and OrderCalcMargin to respect account's symbol cash value. A margin estimate is not a broker execution guarantee; some hedge/netting structures require OrderCheck and additional parity.

Daily account history is refreshed at most once per configured interval (default 5s), or on a new deal. The 1-second timer checks market/account risk and 30s stop-duration independently of ticks. When hard-halted, attempts to flatten only positions with this EA magic on XAUUSD are made; other EAs' positions are included in the account risk metric but are NOT force-closed by this EA.

CAUTION: default percentages are **experimental risk ceilings, not tuned for account size or trading volume**. Even a profitable 1,400-trade/day strategy can hit a strict gross-loss budget due to many small losing trades and commissions. The manager must measure the gross loss distribution and set maximum affordable throughput; it cannot promise full original volume and strictly bounded gross losses simultaneously at every balance.

## Indicator score, and why it is *not* the trained AUC model
For original directional side s in {+1,-1}:
- d = clamp(s*(+DI - -DI)/10,-1,1)
- e = clamp(s*(EMA_closed - EMA_prior)/(0.08*ATR_M1),-1,1)
- q = clamp(s*(most recent completed bid close - 3 observed completed closes earlier)/0.12,-1,1)
- S = 0.45 d + 0.35 e + 0.20 q
The quote seconds must be recent and the older sequence cannot span an excessive gap. The completed M1 bar must be recent too.
Default InpR9M1ShadowEnabled=true; this changes no entries. Default InpR9M1RescueEnabled=false. Enabling rescue would allow a trade previously rejected by original S1 if ADX, directional DI and S thresholds pass. This has **no demonstrated positive expectancy**. It must stay OFF until causal replay, tests and OOS acceptance.

## Quote-side price geometry for 1.75 cash target
Given actual modeled BUY Ask (or SELL Bid) and broker/account cash P&L per one XAUUSD quoted-price dollar K, required liquidation-side price improvement is at least
delta_P = (target_account_cash + assumed_roundtrip_cost_account_cash)/K.
Compute BUY exit using Bid and SELL exit using Ask. Do NOT charge the starting spread twice. Stop-loss exposure uses actual initial stop quote and OrderCalcProfit. Account currency must be USD before treating the target as "US$1.75"; otherwise it is 1.75 units of account currency and must be converted separately.
This is a feasible price SCENARIO, not a probability, a live target order, or an assertion that current trade paths hit it. Inputs: target=1.75 account cash, assumed cost=0.20 cash; both need broker calibration. Cash geometry shadow and native M1 indicators are lightweight; neither writes tick logs.

## Companion source-ordinal feasibility evaluator (separate research-only branch)
Source: https://github.com/AnhTranHarris/gold-MUWHAHA-miner/blob/carson/r9-v193-coinexx-cash175-feasibility-20261113/research/coinexx_r9_chronological/minute60_competing_hazards/src/r9_cash175_feasibility.py
- Reuses EXISTING first_passage_actions and frozen entry ordinals and month receipts; no new causal tick engine or tick archive.
- Reads the original Coinexx month and outputs only a small stdout JSON summary: how many frozen R9 original-direction opportunities hit an executable quote-side account-cash target before a hypothesized original initial static stop within 30s. Explicitly labels quote gaps/censored cases.
- This is an optimistic STATIC STOP research diagnostic, not the original path-dependent dynamic R9 trail or actual trade ledger. It cannot supply 1.75 NET completed-trade averages by itself.
- The exact original preexisting monthly .npz and matching Coinexx original raw are needed for real results. There are NO such raw tick files in this current sandbox; do not invent Jan-Sep performance numbers.
- No new data outputs or regenerated libraries are required.

## Acceptance & next patch
1. Compile entire EA in Coinexx MT5 build. Verify broker AccountInfo currency, session offset and symbol contract. MetaEditor was NOT available in this research environment; MQL5 compilation remains UNVERIFIED.
2. Test day rollover, EA restart/terminal restart, cash charge history, BUY/SELL stop-to-account-cash conversion, concurrent strategies, high daily deal count, free-margin and loss-budget trip, risk lock persistence, timer close after no ticks, weekend/illiquid periods and broker freeze/stop levels.
3. Verify original entry/hold/exit trade behavior when optional rescue/observational cash shadow are disabled; all deviations due to the protection patch must be explicitly accounted for. Run real-tick MT5 Strategy Tester and broker demo; terminal OnTick is not a guaranteed lossless replication of source events.
4. Report whole-system every-month sessions, complete executed trade count, realistic net realized cash/trade after all costs, average holding <=30s, p95/p99, maximum exposure, gross cash loss day, peak-to-trough drawdown, stop price fill residuals and execution failure rate.
5. For native-indicator rescue and eventual hazard/optimal-stopping models: pre-register train/evaluation splits, no false claims of OOS on exposed Jan-Sep, disable every experimental gate until materially positive incremental after-cost economics AND preserved high throughput. Without independent later Coinexx data, no untouched OOS claim is possible.
6. Portfolio hard halt mitigates further entries and may attempt to close own positions; it cannot guarantee a fixed maximum loss during quote gaps, market closure, slippage, off-terminal trading or server reject. Across multiple independent MT5 terminals the terminal global variable lock is NOT shared, although each connected terminal reads account history/equity.

## References
MQL5 OnTimer https://www.mql5.com/en/docs/event_handlers/ontimer
MQL5 OnTradeTransaction https://www.mql5.com/en/docs/event_handlers/ontradetransaction
MQL5 HistorySelect https://www.mql5.com/en/docs/trading/historyselect
MQL5 Deal Properties https://www.mql5.com/en/docs/constants/tradingconstants/dealproperties
MQL5 iADX https://www.mql5.com/en/docs/indicators/iadx
MQL5 iMA https://www.mql5.com/en/docs/indicators/ima
MQL5 OrderCalcProfit https://www.mql5.com/en/docs/trading/ordercalcprofit
MQL5 OrderCalcMargin https://www.mql5.com/en/docs/trading/ordercalcmargin
