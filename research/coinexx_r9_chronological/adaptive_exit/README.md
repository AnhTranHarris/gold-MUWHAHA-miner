# R9 v1.94 — Coinexx-only adaptive hold / trail research

**Status: Python-only ON-POLICY research code and passing synthetic CI. No MT5 source change, no full-month adaptive Coinexx backtest or broker execution certification.** The user-compiled MT5 standalone R9 v1.94 checkpoint remains preserved at 813baf96f2b381be5fc7896aac8b08a966114948; critical R9 v1.90 rollback remains at 8729a6345655a7b4ea31facc81982004ee2b8921.

## Audit and economic goal

The original R9 Python engine and exact v1.94 EA set BUY initial SL at Bid−$0.30 XAU quoted price, SELL at Ask+$0.30; activate trailing after $0.10 favorable quoted movement from actual fill; hold trail $0.03 behind current liquidation-side quote, respect broker minimum stops, and request 30sec timeout. Each close changes opposite same-minute rearming and future entries, so one-off frozen trade exit re-labeling is insufficient.

The previous original-Coinexx January source-ordinal study verified 7,699,274 rows and 32,179 original positions, mean quote-side signed price return −0.1881 XAU quote dollars per trade BEFORE additional fees, average hold 5.82sec, and 94/32,179 hitting an illustrative cash 1.75 goal before the original R9 exit. A previous train-only Aalen–Johansen entry-risk model with the original exit path found no positive utility for its January evaluation, so simply applying a positive-utility gate would eliminate high-volume trading.

**Success criterion is realized net account-currency gains after all modeled spread, commissions, fees, slippage, and bounded account risk, by ACTUAL source entry-hour, with meaningful trade volume and mean holding <=30sec. 1.75 AVERAGE net cash/trade is aspirational, not a forced per-position take-profit level.**

## Actual software built

- research/coinexx_r9_chronological/adaptive_exit/src/adaptive_policy.py — subclasses the existing source-exact coinexx_r9.R9HybridGateBaseline engine; preserves broker stop BEFORE quote management, minute cycles, completed M5 ATR, S1 entry gate, original trade state, and same-minute rearms. Different policies independently reprocess each quote and thus independently create NEW subsequent entries.
- research/coinexx_r9_chronological/adaptive_exit/src/cli.py — streams ORIGINAL unchanged Coinexx .csv.gz through baseline and alternatives ONCE. No new raw tick or OHLC libraries, no derived feature archives. Output stdout JSON, with optional one small JSON receipt.
- Base policy baseline: exact original R9 (no override).
- cost_trail: original initial protective stop plus after-cost activation and causal spread/realized-noise trailing with monotonic stop tightening.
- staged_harvest: cost_trail plus bounded early harvest only when observed liquidation cash AFTER additional expenses is positive AND past-only continuation index has turned adverse; original 30-sec maximum retained.
- experimental_wide_stop: separate *higher-risk*, explicitly opt-in initial SL widening ablation. Requires maximum hypothetical cash loss to widened stop <= configured cap. Not a recommended default or authorized live risk limit.

Only original quote-time price data is used for historical market observations: Bid, Ask, timestamps and source order. The existing v1.94 high-AUC 155-feature model is not silently misused as a cash probability; its original target differs from realized trailing exit economics.

## Equations (all market distances in exact 0.01-XAU quote units)

Define a = +1 BUY, -1 SELL, P_entry = original ASK BUY or BID SELL, L_t = current BID BUY or ASK SELL; K = broker-verified account cash per +$1.00 XAU price movement at 0.01 lot; C = EXTRA full-roundtrip account-cash fee/slippage beyond the already-incorporated Bid/Ask spread.

    pi_net(t) = K*a*(L_t - P_entry) - C

Past-only completed one-second midquote-price movement volatility is:

    sigma_1s = sqrt( mean( (mid_close_s - mid_close_(s-1))^2 ) )

M1 10-bar StdDev of COMPLETED Bid close levels and M5 completed Wilder ATR14 act as a weak regime scaling, not fabricated high-resolution volume data:

    sigma_eff = sigma_1s * (1 + gamma * min(2, StdDev_M1_10closed/ATR_M5_14closed))

When 1s quote observations are unavailable, prior completed M5 ATR/sqrt(300) is explicitly marked as a SLOW fallback. If the last quote gap exceeds 2500ms, revert to original R9 management, not a future-filled model. No incomplete M1 bar information enters these slow indicator proxies.

Causal activation and trailing price distance:

    activate_cents = max(R9_original_10c, ceil[100*(C+small_positive_buffer)/K], ceil[beta*sigma_eff])
    trail_cents = max(R9_original_3c, ceil[alpha*current_spread], ceil[beta*sigma_eff], broker_stop_min+tick)
    trail_cents = min(configured_price_cap,trail_cents) unless broker minimum dominates

Always tighten monotonically: BUY new stop must be above old SL; SELL new stop below old SL. Never widen a stop automatically.

Dimensional continuation/reversion INDEX, not a trained probability:

    I_t = 0.60*tanh(a * recent_mid_displacement / (2*max(1,sigma_1s)))
          +0.40*a*completed_quote_path_efficiency
          -0.20*positive_spread_shock
          +w_M1_EMA*tanh(a*last_completed_M1_EMA20_slope/max(1,ATR_M5))

For staged_harvest only, request liquidation at current executable quote if age>=4 sec, pi_net>=0.10 account cash, AND I_t<−0.10. These constants are predeclared, NOT trained or certified as profitable. No positive cash opportunity is claimed simply because a quote passed a score.

Experimental wide initial stop (ONLY explicit user opt-in) is a separate causal risk ablation:

    d0_cents = min(60, max(original_30c, ceil[2*spread + 1.25*sigma_1s]))
    allow only if modeled net loss at widened stop >= -MAX_INITIAL_CASH_RISK

A *calibrated* later quant optimal-stopping model should use policy-specific trained risks from PRIOR months, not unaltered baseline hazards from exits that the alternative policy prevents. At quote t, actions are EXIT_NOW, HOLD_CURRENT_STOP and TIGHTEN_STOP:

    Q_exit(t,x) = pi_net(t)
    Q_continue(t,x,action) =
        sum_j cause_incidence_j(remaining_life|x,action)*E[net_cash_j|x,action]
        -lambda*CVaR95_future_loss(x,action)
        -eta*next-opportunity-occupancy_cost(x,action)

The model is NOT calibrated here: the implemented index is a causal heuristic to be judged by full on-policy replay before any conditional hazard fit and deployment. No promotion to a live profit optimizer based on this file alone.

## Native MQL5 indicator audit and Coinexx-only proxies

| Native MT5 candidate | Historically reconstructible? | Correct role |
|---|---|---|
| iATR PERIOD_M5 14, optional M1 14 | Yes, completed Bid-price OHLC | Already used by R9 gate; slow realized regime scaling, not tick volatility |
| iStdDev PERIOD_M1 10, SMA close | Yes, completed Bid-close series | Small slow volatility modifier; Python includes causal reference and ablation weight |
| iMA PERIOD_M1 EMA20 PRICE_CLOSE | Yes, completed Bid-close series | Small slow trend continuation modifier; Python includes causal reference and ablation weight |
| iADX/iADXWilder M1 +DI/-DI | Yes, completed Bid OHLC | Existing v1.94 indicator observations; future ablation for runner vs chop, not invented probability |
| iAMA OR iFrAMA M1 | Yes, completed Bid closes | Optional slower trend benchmark, test against EMA instead of stacking correlated indicators |
| iSAR M1 | Yes completed OHLC | Only a shadow stop reference, not direct 30-second execution stop |
| iVolumes(VOLUME_TICK) | Broker quote update COUNT proxy only | Quote intensity, NOT executed traded contract volume; exact native-vs-source count parity uncertain |
| iOBV/iMFI with tick volume | Only price × quote-count proxy | Highly derivative, not true order flow; low research priority |
| Genuine VWAP with traded units, VPIN, L2 microprice/depth imbalance, signed aggressor order flow | NO | Cannot reconstruct; never claim proxy equals actual volume or depth |

A native M1 iADX, Bollinger bands or moving average may lag the historic mean original 5.82-second hold. For sub-30-second decisions, use causal quote-side realized noise, spread freshness/changes, sign/efficiency of quote revisions and liquidation cash before slow M1 context. Raw Coinexx Last, volume, volume_real were zero across audited Jan-Sep market rows; native iVolumes real-volume requests cannot fill this gap. Native price-series parity in Coinexx MT5 must be tested before transplanting Python M1 calculations into MQ5.

## Run on original local Coinexx, no downloads/rebuilds

Checkout branch carson/r9-v194-adaptive-hold-trail-python-20261113 on your local research machine. At repo root, using the existing original January Coinexx source gzip:

    python research/coinexx_r9_chronological/adaptive_exit/src/cli.py --ticks "C:\Coinexx\XAUUSD_MT5_BROKER_2026_01_ticks_ALL.csv.gz" --expected-source-sha256 1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8 --account-currency USD --cash-per-one-xau-dollar 1.0 --round-trip-cost-cash 0.20 --output "r9_adaptive_january_small_receipt.json"

K=1.0 and C=0.20 in that example are DEMONSTRATION values and MUST be replaced with actual broker OrderCalcProfit and account fee data before economic claims. Every policy gets identical exact-ordinal market ticks in a single read; each arm maintains independent positions, execution prices, stops, fee accounting, opposite rearms and subsequent entries. No raw data output. A bounded --max-ticks 300000 run is a SMOKE CHECK only and is explicitly marked truncated; cannot establish monthly profitability.

Ablate completed-M1 indicators by setting --m1-std-weight 0 --m1-ema-weight 0 and comparing full-system outcome on the same frozen calendar. The optional experimental-wide-stop mode requires BOTH --policies baseline cost_trail staged_harvest experimental_wide_stop and --allow-wider-initial-stop; do not run it without explicit risk capacity.

## Pass/fail before changing any MT5 EA

1. Exact disabled-policy baseline entry/exit source ordinals match original pinned Coinexx trade ledger; synthetic CI parity alone is not 7.7M-tick parity.
2. For all 9 existing source months, each policy changes positions and after-cost net/account-hour on its own, not by frozen trade labels. Split train/evaluation chronologically; Jan-Sep were development-exposed, NOT prospective untouched OOS.
3. Compare total/trade/hour after-cost cash, trade-count retention, gross daily loss, drawdown, p95/p99 hold, worst day, fees, median/worst broker stop geometry and fraction of stop/timeout/harvest exits. Report unprofitable hours and hour/day confidence by resampling entire days.
4. Verify Coinexx broker contract K, lot, account currency, commission, slippage and order rejection. Broker stop/freeze and MetaTrader 1-second timer behavior cannot be fully derived from quote logs.
5. Account-wide v1.94 governor (gross losses + fees + floating loss, hard drawdown, margin, multi-EA trading) remains outside this phase; the simulator says so explicitly. A separate faithful portfolio-capacity run is MANDATORY before any release decision.
6. No original EA source modifications. R9 v1.94 and original v1.90 are both preserved and maintain rollback safety.

Official docs: https://www.mql5.com/en/docs/indicators/iatr ; https://www.mql5.com/en/docs/indicators/istddev ; https://www.mql5.com/en/docs/indicators/iadx ; https://www.mql5.com/en/docs/indicators/iama ; https://www.mql5.com/en/docs/indicators/iframa ; https://www.mql5.com/en/docs/indicators/ivolumes .
