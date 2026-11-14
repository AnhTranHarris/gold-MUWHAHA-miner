# R9 v1.94 — Variable-horizon, net-cash profit ladder (research checkpoint)

**2026-11-14 | PYTHON RESEARCH DESIGN ONLY | NOT A COMPILED EA, BACKTEST, OR PROFITABLE STRATEGY.**

The owner revised the original human-selected 30-second maximum holding rule to irregular holding duration, desired +0.50 to +1.75 **realized net account-currency profit** after brokerage charges, an intended per-position $2 **absolute loss and peak-to-current mark-to-market cash drawdown ceiling**, and a 25% **account capital-loss emergency ceiling**. No production R9 .mq5, trading account, original dataset, or rollback is changed here. The $2, +$0.50 and +$1.75 are account-currency values, not XAUUSD quoted-price movements.

## Source-verified current EA mechanics

Compiled standalone source from commit `813baf96f2b381be5fc7896aac8b08a966114948`, `Experts/Advisors/GWM_EA/r9_v1_94.mq5`: fixed trailing activation +$0.10 XAU quoted price, $0.03 trailing distance, original stop $0.30 from liquidation quote, 30-second timeout. Existing account loss governor defaults: 4% starting daily gross loss budget, 12% maximum budget, 25% gross profit recycling, 10% peak-equity drawdown halt, margin controls. The owner requested 25% *maximum account loss* and this design treats it as a **new absolute capital floor**. It DOES NOT relax the existing tighter 10% peak-equity account halt or 4–12% daily budgets. Those independent controls remain part of the acceptance contract. R9 v1.90 exact critical rollback commit `8729a6345655a7b4ea31facc81982004ee2b8921` remains untouched.

## Interpretation of $2 drawdown

For conservatism the $2 nominal cap is applied BOTH to (a) estimated **net mark-to-market loss from entry** at the current liquidation-side quote and (b) **peak net marked cash minus current net marked cash** within an individual position. At entry the original SL is retained if tighter. An original SL that implies greater than $2 loss under broker-calibrated sizing/costs causes a new entry to be blocked; existing SL is never automatically widened toward $2. Execution gaps, stop slippage, fee drift and network delays can make actual loss exceed the nominal limit. Do not market this as guaranteed maximum loss.

## Cash accounting

Let side s be +1 BUY or -1 SELL. E is actual entry Ask for BUY or actual entry Bid for SELL, L(t) is current Bid for BUY or Ask for SELL. Let K be **broker verified** account-currency amount for an XAUUSD $1.00 price movement for this position size; C is additional *roundtrip* costs not already paid in quote-side bid/ask (commissions, fees, realistic slippage assumptions):

    net(t) = s × [L(t) - E] × K - C

The net-profit quote-side exit level for cash g is:

    P_exit(g) = E + s × (g + C) / K

In the previous illustrative but **unverified** K=1.00, C=0.20 scenario: +$0.50 cash requires favorable executable-price move of $0.70 XAUUSD; +$1.75 requires $1.95. Since this is larger than original R9 $0.10 trail activation and $0.30 initial-stop width, the new rule is NOT a minor adjustment of the old trailing stop. Original Coinexx nine-month R9 simulated gross quote-side expectancy was NEGATIVE even with zero extra roundtrip fee; no positive expectancy is presumed here.

## Proposed causal decision process, no fixed take-profit time

1. Original R9 minute bracket, M5 ATR/session/S1 gating, single-position mechanics and same-minute rearm remain unchanged at entry. Preserve volume by not vetoing entries solely because the original 5-second AUC score is missing.
2. Never widen the original initial protective stop. Block entries violating the intended $2 net stop-risk ceiling, existing daily gross-loss capacity, available margin or other existing governor controls.
3. On every observed quote, calculate hypothetical liquidation net cash. Request protective close when net cash <= -$2, peak-to-current marked net cash drawdown >= $2, or existing account governor locks. Execute the ORIGINAL tighter broker-side stop whenever applicable. **None guarantees a $2 fill**.
4. In positive-cash region `[+$0.50,+$1.75)`, take profit now unless there is a separate, independently validated **lower confidence bound of policy-specific HOLD-minus-EXIT economic utility** above a predeclared margin. P5 cash first-cause favorable/adverse probabilities serve only as supporting *entry-time* evidence for ages <=5s. They are NOT lifetime hold probabilities or expected dollar returns. No verified continuation advantage = realize cash now.
5. For an eligible early runner only, request a tighter protective SL whose *idealized stop fill* retains at least +$0.50 net after costs and whose legal placement is accepted given SYMBOL_TRADE_STOPS_LEVEL, SYMBOL_TRADE_FREEZE_LEVEL and tick size. If current stop already locks the floor, keep it; if the broker cannot legally lock that floor, take cash now. Ratchet the net floor upward after favorable movement; never loosen current stop.
6. At/above +$1.75 net, take profit rather than arbitrarily extending holding. That is a user profit-range objective, NOT a trained optimum. A trade may exit with less than +$0.50 (including a loss) from adverse reversal, risk limits, broker stop or emergency timeout. Do NOT imply every trade will be a winner.
7. There is no profit-seeking 30s deadline. A **research-only 120s stranded-position failsafe** is a bounded operational safety assumption, not a forecast of optimal holding time. It must be re-evaluated against new quote-gap, rearm and occupancy evidence before MT5 deployment. No time-based forced profitable exit is possible.

The completed previous landmark continuation-value experiment demonstrated that the original P5 score did not add reliable hold-versus-exit utility at 1s or 3s. Therefore the working prototype deliberately **fails closed to immediate profit harvest at >=+$0.50** when no independently validated continuation-value lower bound exists. This makes it a testable baseline policy, not a falsely claimed trained AI runner.

## Account capital 25% floor: do not undo 10% peak-DD governor

Let E0 be opening reference capital, peak(t) observed peak equity, equity(t) actual account equity:

    emergency_capital_halt = equity(t) <= 0.75 × E0
    preserve_existing_peak_halt = equity(t) <= 0.90 × peak(t)
    preserve_daily_gross_halt = gross_loss_consumed >= original daily_budget

If ANY halt is true, block new entries and request the appropriate original EA portfolio-protective handling. These checks complement, not replace, margin and gross-loss controls. Important scope limitation: the current EA uses terminal-scoped GlobalVariable state, not broker-global coordination across distinct MT5 terminals. Historical Coinexx quote files do NOT provide account equity, deal commissions or all-EA positions.

## Pilot implementation and tests

`cash_ladder.py` is a **pure Python decision layer** with `CashLadderSpec`, `CurrentPosition`, `AccountSnapshot`, `ConditionalEvidence`, `VariableCashHorizonPolicy`; its return actions are `HOLD`, `CLOSE_NOW`, `TIGHTEN_STOP`, `BLOCK_ENTRY` and never send an order. It has no raw tick or feature-file IO. `tests/test_cash_ladder.py` validates exactly 16 bounded synthetic tests including BUY Ask→Bid net cash, SELL Bid→Ask, normal cash harvest, $1.75 target, legal profit stop constraints, model evidence freshness, $2 position loss and drawdown, account 10% vs 25% ceiling, daily budget preservation, stale quote and >30s variable holding. Tests establish unit correctness only, not financial efficacy.

## Single next scientific test — not a 100-parameter sweep

Reuse the EXISTING original Coinexx chronological Python R9 engine (no new tick engine), stream each original quote once with independent position/rearm states, and compare exactly THREE policies:

- Original R9 baseline with original 30s timeout and original strict account-loss controls.
- $0.50 cash-harvest / variable-horizon research arm with original initial stop, no unvalidated model runner.
- Same cash-harvest arm with **only previously held-out policy-specific continuation-value evidence** permitting a runner; do not use the original 5s P5 by itself to extend a trade.

Source-exact baseline must first reproduce frozen 303,934 historical R9 entries/exits; otherwise no policy metrics are accepted. Score **whole-system modeled realized net per source-active hour, net per completed trade, 95% monthly trade retention, mean/p95/p99 holding time, gross loss, daily/hourly downside, monthly equity peak DD, actual quote gap, age, and opposite-side rearm counts**. Preserve original broker fee/contract calibration unknowns explicitly and run fee/slippage sensitivity. A 25% account cap cannot be faithfully tested without account snapshots or explicitly reported conservative assumptions. Full stop/timeout behavior across quote gaps and broker slippage must be treated as potential failures. Historical Jan-Sep previously research-exposed and cannot certify new unseen OOS.

Do not promote any exit-policy source change to production MT5 until after-cost profit/hour and gross-loss controls beat baseline at acceptable trade volume. The goal is positive **realized** net P&L, not an AUC or price-touch count.

MetaQuotes documentation: https://www.mql5.com/en/docs/trading/ordercalcprofit , https://www.mql5.com/en/docs/constants/environment_state/marketinfoconstants , https://www.mql5.com/en/docs/event_handlers/ontradetransaction .