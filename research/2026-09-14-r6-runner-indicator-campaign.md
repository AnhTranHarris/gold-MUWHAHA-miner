# R6 runner / indicator campaign — 2026-09-14

## Objective
Preserve or increase R5 net profit while reducing gross loss, with special attention to runner management and forum-supported trend/volatility qualifiers.

## External hypothesis cross-check
Sources reviewed included Gold Hunter V8 on Myfxbook, Reddit XAUUSD breakout/EA discussions, ForexFactory gold breakout threads, and TradingView gold/Asian-range breakout systems.

Recurring public hypotheses:
- ATR for volatility and dynamic exits.
- ADX for trend-strength qualification.
- EMA trend alignment for breakout continuation.
- Asian-range context for London/NY breakout quality.
- Candle-body strength vs ATR to reject fake breaks.
- Wider/ATR-based trailing for proven trend runners.

These are community hypotheses, not accepted facts. They were tested against the Coinexx archive rather than copied directly.

## Python campaign
Dataset: Coinexx XAUUSD M1 archive, 2020-01 through 2026-08, with completed-M5 features and R5-equivalent session/spread/ATR gate.

### Runner sweep
Tested context-qualified wider trailing, delayed trailing activation, break-even-then-runner designs, and ATR-scaled trailing using combinations of:
- M5 ADX thresholds 20–30
- M5 ATR thresholds ~3–4+
- M5 EMA20/EMA50 alignment and EMA slope
- London / overlap / New York session membership
- Asian-range normalization

Result: none of the runner/indicator variants beat plain R5 in the full-history ranking proxy. The best variants were slightly worse in net capture with no compensating gross-loss improvement.

Conclusion: do not add EMA/ADX/ATR runner complexity to the MT5 candidate yet.

### Fixed-risk neighborhood
A focused sweep around R5 showed the hard stop was the dominant remaining lever. In the M1 ranking proxy, reducing the hard stop from $0.30 to $0.20 while retaining 8/8 trailing reduced gross loss by roughly 29% and slightly increased net capture. A $0.15 stop screened even better, but this is too close to gold microstructure/spread noise for promotion directly from M1 OHLC.

### Year-by-year result
The 20-pip stop improved the proxy relative to the 30-pip R5 stop in every calendar year 2020–2026, primarily through lower gross loss. The 15-pip stop also ranked higher but is intentionally not promoted without a 20-pip real-tick stepping stone.

## Promotion decision
Promote one conservative MT5 candidate only:
- Gap = 100
- Stop loss = 20
- Trail = 8
- Trail activation = 8
- All R5 ATR/session/spread logic unchanged
- No additional EMA/ADX/candle/news/Asian entry filter

Reason: the forum-supported runner ideas failed our own screening, while the stop-tail compression was consistent across years. ForexFactory gold discussions also warn that overly tight stops and NY-open spread/fake-break behavior can destroy breakout edge, which is why 20 pips is promoted before the more aggressive 15-pip research result.

## Certification rule
MT5 real ticks remain authoritative. R6 advances only if it preserves or improves R5 net profit while materially reducing R5 gross loss and not materially degrading drawdown, PF, or expectancy.
