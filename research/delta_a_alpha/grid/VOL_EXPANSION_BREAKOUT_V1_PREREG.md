# VOL_EXPANSION_BREAKOUT_V1 — January Candidate Preregistration

**Status:** FROZEN BEFORE PHYSICAL SINGLE-OWNER VERIFICATION
**Lineage:** R9 Delta-A-alpha Grid System

## Role

This is the first candidate mode to emerge from January discovery. It is a sparse volatility-expansion specialist mode inside the system-wide grid/lattice, not the whole grid system.

## Frozen opportunity clock

- XAUUSD only.
- DUKAS_COINEXX_LIKE_P75 ordered-tick surface.
- Elastic grid alpha = 0.50 research-clock geometry.
- Completed-M1 ATR14 controls active grid spacing.
- gap = max($1.00, 0.50 * ATR14_M1), clamped $1-$8, quantized $0.25, 10% hysteresis.
- Fixed lot = 0.01.
- No Martingale, no loss-dependent sizing, no averaging.

## Volatility-expansion regime

Use completed M1 true-range history only.

- fast volatility = ATR14_M1.
- slow volatility = ATR240_M1.
- expansion_ratio = ATR14_M1 / ATR240_M1.

Primary regime gate:
- expansion_ratio >= 1.75.

Sensitivity lane only:
- expansion_ratio >= 2.00.

The 1.75 threshold is selected as the broader January knee, not as an optimized maximum.

## Causal breakout ownership

At a virtual elastic-grid event:
1. record event-origin midpoint m0 and active elastic gap G;
2. observe for at most 3 seconds;
3. set two causal confirmation barriers: m0 + G and m0 - G;
4. whichever barrier is touched first owns direction;
5. if neither barrier is touched within 3 seconds, abstain;
6. enter only after the confirmation barrier is actually reached, at executable Bid/Ask.

This means the source grid no longer decides direction. The lattice identifies the event; price must demonstrate breakout ownership.

## Risk / thesis invalidation

- stop = original event midpoint m0, using executable side crossing;
- target = 1.5 * active elastic gap from actual entry;
- maximum trade horizon = 5 minutes after entry;
- $0.02 round-trip commission;
- no recovery flip in V1;
- no concurrent averaging ladder.

The event origin is the thesis boundary: after a full one-gap breakout confirmation, returning through the originating event level invalidates the breakout thesis.

## January discovery evidence

Event-level shadow tests, before single-owner overlap enforcement:

At expansion_ratio >= 1.75 with target 1.5*gap:
- full January PF ~1.253;
- expected payoff ~+$0.850/event;
- discovery PF ~1.046, expected ~+$0.063;
- validation PF ~1.301, expected ~+$1.544;
- about 239 accepted events.

At expansion_ratio >= 2.00 sensitivity:
- full January PF ~1.304;
- expected payoff ~+$1.152/event;
- discovery PF ~1.144, expected ~+$0.206;
- validation PF ~1.331, expected ~+$1.732;
- about 171 accepted events.

The neighborhood from roughly 1.75 through 2.0 is positive in both chronological January segments. Lower expansion thresholds deteriorate materially. This supports a regime effect rather than a single-point threshold artifact.

## Required next gate

Before Jan-Jul validation, build an account-level physical single-owner January replay:
- maximum one active grid-owned trade at a time;
- ignore or shadow new candidate events while owned;
- exact Bid/Ask execution;
- mark-to-market equity path;
- balance and equity drawdown;
- trade overlap/suppression counts;
- $100/$200/$300 survivability diagnostics;
- same fixed 0.01 lot.

Only if the single-owner January replay remains positive may V1 advance to Jan-Jul month-by-month validation.

## Anti-overfit rule

Do not tune 1.75 into dozens of decimal thresholds.
Do not optimize target multipliers around 1.5.
Use >=2.0 only as a sensitivity check.
Any later refinement must answer a structural failure observed out of sample.

August remains sealed. Main delta remains read-only. MQL5 remains unauthorized.
