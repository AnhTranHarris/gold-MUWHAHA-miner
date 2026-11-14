# R9 v1.94 — 15-second basket / 15- and 30-second breakout research

**2026-11-14 · Python-only source-exact Coinexx quote experiment · NOT production MT5; NO broker-cost calibration.**

## Owner-approved research change
- Replace the one-minute entry **basket/reset** with a 15-second basket; compare separate 15s and 30s completed-quote breakout windows, not a guessed hard entry time.
- Keep original R9 market order mechanism, S1 quality gate, completed-M5 ATR/session/spread gates, 0.01 lot, original initial protective stop, and risk caps as frozen comparators.
- Exit policy experiment: **$0.50 NET liquidation objective**, stretch **$1.75 NET**, no forced $0.10 minimum harvest, and original tighter stop preserved. Per-position $2 intended maximum loss and 25% outer account emergency ceiling do NOT relax the existing 10% peak-equity drawdown and daily 4%/12% gross loss governor limits.
- The inherited original 30s fixed hold remains intact on breakout-only control arms. Variable-horizon cash arms use the separately audited cash ladder with a 120s emergency backstop. This ablates breakout changes from holding changes.
- Do not misrepresent the 155-feature model as usable on new 15-second entries: frozen training scores exist at original R9 minute-entry source ordinals. **No original high-AUC runner is active** until all 155 features are regenerated in real time with exact as-of parity and the HOLD-versus-EXIT value is validated. Existing five-second scientific +$0.10 event label is not the desired trading profit.

## Why the entry geometry is different

Old R9 tests ASK against a midpoint-anchored high and BID against its low. The effective midpoint required for a BUY is `0.15 - spread/2`, changing with spread. The research replacement tests **midpoint against midpoint**:

- For quote second `t`, `B(t)=15*floor(t/15)` and `M(t)=(Bid_t+Ask_t)/2`. A new basket anchors `M_B` at its **first observed quote**, independently of wallclock minute starts.
- BUY requires `M_t >= M_B + delta`; SELL requires `M_t <= M_B - delta`. Predeclared experiment `delta=0.10 XAU quote price` (10 cents) is a **breakout movement requirement, not a profit-taking amount**. Tests must fail if actual cash profit remains below $0.50 at liquidation. This parameter is not tuned using held-out results.
- For lookback `h=15` or `h=30` seconds, let `C_h(t)` be **only completed observed 1-second BID/ASK simultaneous CLOSE** midpoints with source second `t-h <= sec < t`. BUY also needs `M_t >= max(C_h(t)) + 0.01`; SELL needs `M_t <= min(C_h(t)) - 0.01`. No future quote or current unfinished-second high enters the window.
- At least four completed observed seconds are required for h15, eight for h30; latest completed observed second must be <=2s old, otherwise abstain.
- Original S1 causal quote-second displacement/range/efficiency, M5 Wilder ATR/session regime, broker spreads and account governor still apply. The original S1 quote-second sequence still allows non-consecutive observed seconds; strict freshness is separately enforced for the new breakout.
- Opposite-side rearming occurs **only if the entry and close both belong to the current 15-second basket**. A position crossing a basket boundary does not force a stale opposite rearm into a new basket. New basket starts both sides fresh. Exact original R9 baseline retains its existing minute semantics and must reproduce its full archived trade ledger.

## Test arms

1. `original`: fully unchanged source-exact R9 Python baseline, no cash-ladder modifications; full archived original trade ledger parity required for any complete-month result.
2. `15b_15break_original_exit`: shorter basket, 15s breakout, original 30s hold/trail/stop.
3. `15b_30break_original_exit`: shorter basket, 30s breakout, original 30s hold/trail/stop.
4. `15b_15break_cash050`: shorter basket, 15s breakout, $0.50 minimum harvest, $1.75 stretch, $2 intention, variable holding.
5. `15b_30break_cash050`: shorter basket, 30s breakout, same cash ladder.
6. `15b_30break_nested_trend_probe` **optional**: independent quote-only 3/10/30/120s trend persistence probe, **not** a validated AI runner. Original published P5 AUC does not certify this arm.

The MARKET quote and completed-second ATR/S1 context are shared as read-only state (original unmodified market pipeline); each arm has independent `position`, `pending_mode`, basket resets, rearms, fills, exits and account accounting. The raw original Coinexx `.csv.gz` is streamed exactly once, preserving duplicate-ms source order. There is no second tick reconstruction engine or rebuilt data archive.

## Source and risk assumptions

- The January original Coinexx gzip SHA256 is `1307a75df5d635678de7691908600090a552f38543e0512187dcd7b37fbc66b8`; original full 9-month source hashes and frozen trades are in `R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip`.
- Quote-side cash `Pi=K*s*(L_t-E)-C`, BUY entry Ask/exit Bid and SELL entry Bid/exit Ask. K=1.0 USD per $1 quoted-price move at 0.01 lot and additional C=0.20 are ILLUSTRATIVE; real broker `OrderCalcProfit`, lot normalization, actual fees, latency/requotes/slippage not observed. The spreads are already paid once through quotes.
- All 5/6 arms must be judged by **net modeled cash/hour, percent of completed trades >$0.50 NET, 95% monthly trade retention, gross loss, left-tail CVaR, max account drawdown, holding duration and rearm behavior**, not AUC or selected winner returns alone. A strategy may fail even if more trades close at $0.50. Account-wide governor mode, if run, must be compared to a *same-governor* original baseline, not the ungoverned frozen original control.
- Existing 10% peak-equity and daily gross-loss limits remain; a $2/position or 25% emergency ceiling is NOT permission to enlarge original stops.
- January–September have been extensively researched before, so chronological testing there is retrospective and not genuinely unseen OOS.

## Native MetaTrader indicator compatibility

**15-second and 30-second bars are NOT native standard MT5 timeframes.** Use a dedicated bounded quote-ring builder in any later EA, with the same source-ordinal and completed-second causal rules (never interpolate beyond missing quotes).

| Feature/indicator | Coinexx-only reconstructible? | Use |
|---|---|---|
| `iATR(PERIOD_M5,14)` shift=1 | YES, original completed M5 OHLC | Retain R9 volatility gate; ablate slow trend context after entry experiment |
| `iADXWilder(PERIOD_M1)` +DI/−DI shift=1 | YES, Bid completed OHLC, warm-up | Persistent trend vs choppy market; SOFT regime covariate, not a hard high-volume veto until paired benefit established |
| `iMA(PERIOD_M1,20, MODE_EMA)` shift=1 | YES Bid completed closes | Slow nested trend orientation |
| `iStdDev(PERIOD_M1,10)` / `iBands` | YES completed closes | Slower noise/compression state; not a substitute for 15s quote volatility |
| `iFrAMA` / `iAMA` | YES after warm-up | Optional alternate adaptive trend, not stacked with EMA by default |
| `iVolumes(...,VOLUME_TICK)` | Quote/tick count proxy only; native parity to logger not guaranteed | Quote-arrival intensity, not executed market volume or order book |
| True VWAP by executed size, real VPIN, signed market order flow, order-book microprice/OFI | NO real volume/depth in Coinexx logger | EXCLUDE. Use spread shock, quote gaps and signed midquote revisions as **proxies**, never relabel them true OFI |

Extra indicators must pass incremental paired ON/OFF market-state tests without dropping >5% of entries or reducing net cash/hour. MetaQuotes documents OnTick coalescing: a slow tick handler can miss quotes available in the research tick tape. A future EA needs an efficient quote ring, completed M1/M5 CopyBuffer, state-machine parity, transaction reconciliation and a real MetaEditor compile before deployment.

## Running against existing files (no dataset copies)

```sh
python quarter_basket/run_quarter_basket.py --data /mnt/data --receipt /mnt/data/R9_P1_Coinexx_9Month_SourceOrdinal_ASOF_CANDIDATE_CACHE_20261113.zip --months 01 --experiment-regime-probe --output /mnt/data/R9_15S_JAN_2026_RESEARCH_SCORECARD.json
```

For a bounded smoke sample add `--max-rows 100000`. A smoke result is **NOT** accepted as monthly performance and marks full original-ledger parity false. Do not publish a 70% success claim before on-policy completed-month and same-governor confirmation.