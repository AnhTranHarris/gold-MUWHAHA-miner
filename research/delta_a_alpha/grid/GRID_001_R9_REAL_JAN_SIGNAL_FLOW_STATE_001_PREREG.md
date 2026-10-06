# GRID-001 R9 REAL January Signal-Flow State 001 — Preregistration

**Unit:** `DAA_GRID_001_R9_REAL_JAN_SIGNAL_FLOW_STATE_001`  
**Status:** FROZEN BEFORE ANALYSIS

## Hypothesis

R9 REAL's own BUY/SELL signals form a high-frequency event stream.

Instead of treating every signal independently, model the recent signal stream as a nested trend-within-trend state:

- fast specialist-flow pressure;
- slower specialist-flow pressure;
- current signal relation to both;
- relation of signal-flow state to the frozen 5m/15m market-state owner.

This is an original Delta-A-alpha mutation inspired by HFT event-time imbalance architecture.

No order-book depth is assumed.

## Causal signal-flow features

All features use **prior R9 signals only** before the current entry.

### S1 — time since previous R9 signal

Frozen bins:
- <1 sec
- 1–3 sec
- 3–10 sec
- 10–30 sec
- >=30 sec

### S2 — same-direction run length

Number of consecutive prior signals including the immediately preceding side, evaluated before current signal.

Current signal state:
- NEW/FLIP: current side differs from prior signal
- RUN_2
- RUN_3_4
- RUN_5_8
- RUN_9_PLUS

### S3 — exponentially decayed signed flow pressure

For prior signals:

`P_tau(t) = sum(side_i * exp(-(t-t_i)/tau))`

Frozen horizons:
- FAST tau = 2 seconds
- SLOW tau = 10 seconds

Evaluate pressure **before adding the current signal**.

Current-signal aligned pressure:

`A_tau = current_side * P_tau`

Frozen states per horizon:
- OPPOSED_STRONG: A <= -2
- OPPOSED: -2 < A < -0.5
- NEUTRAL: -0.5 <= A <= 0.5
- SUPPORT: 0.5 < A < 2
- SUPPORT_STRONG: A >= 2

### S4 — nested signal-flow relation

Using FAST and SLOW sign/state:

- BOTH_SUPPORT
- BOTH_OPPOSE
- FAST_SUPPORT_SLOW_OPPOSE
- FAST_OPPOSE_SLOW_SUPPORT
- FAST_ONLY
- SLOW_ONLY
- NEUTRAL/MIXED

This is the event-flow analogue of trend within trend.

## Frozen cross-state comparisons

Only these interactions are allowed:

1. nested flow state alone;
2. flow state × market owner relation:
   - ALIGNED
   - OPPOSED
   - NEUTRAL
   - CONFLICT;
3. flow state × owner phase:
   - EARLY
   - MATURE
   - EXTENDED / NONE.

No arbitrary post-hoc conjunction search.

## Metrics

For every state:
- trades/share;
- MT5 net;
- deal-level gross profit/loss/PF;
- gross-loss share;
- gross-profit share;
- discovery/validation net;
- hypothetical veto ceiling.

## Preferred breakthrough gate

A signal-flow family is high-leverage if:
- it contains >=20% of canonical R9 REAL January gross loss OR >=20% of net loss;
- it is net-negative in discovery and validation;
- gross-loss share exceeds gross-profit share materially;
- trade share is meaningfully lower than the gross-loss share OR the family exposes a clear routing asymmetry.

This is still diagnostic; no signals are vetoed in this unit.

## HFT/scalping grounding

Public HFT frameworks distinguish:
- event clocks from wall-clock bars;
- alpha/state from risk admission;
- flow imbalance from inventory/risk control.

Delta-A-alpha adapts the event-flow concept to the only causal stream we actually possess here: R9 specialist signals.

No L2/L3 data is invented.

August sealed. Main `delta` read-only. MQL5 unauthorized.
