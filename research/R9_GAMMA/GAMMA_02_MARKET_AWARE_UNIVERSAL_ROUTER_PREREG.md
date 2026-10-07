# GAMMA-02 — Market-Aware Universal Router Preregistration

**Status:** ACTIVE RESEARCH — MONTH-BLIND ROUTER RESET  
**Parent:** carson/r9-gamma-02-velocity-geometry-research @ e866fd5af7f5ec8701f1606765b34b7993439c5c  
**Branch:** carson/r9-gamma-02-market-aware-router-research  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Owner correction

January/February-native discoveries are engine-library evidence, not permission to deploy calendar-month modes.

The deployable router MUST NOT use:
- month number;
- day-of-month;
- week-of-year;
- hardcoded "January/February/etc" mode;
- future labels or retrospective month assignment.

Month boundaries are evaluation partitions only.

## Hard objective

Preserve the high-net opportunity discovered in GAMMA-02 while materially reducing:
- gross loss;
- balance drawdown;
- tick-level equity drawdown;
- regime-dependent collapse.

R9 SYNTH remains the hard benchmark, not a ceremonial reference.

Known exact January R9 SYNTH:
- net +$41,520.82
- 27,980 trades
- PF 23.7154119275
- 87.0908% wins
- +$1.483946 expectancy/trade
- 16.4627 s average hold
- inferred gross loss -$1,827.87 from net/(PF-1)
- inferred gross profit +$43,348.69

Known Jan-Jul R9 SYNTH:
- net +$309,122.85
- gross profit +$325,361.51
- gross loss -$16,238.66
- PF 20.036229
- 219,342 trades
- 87.14% wins
- +$1.409319 expectancy/trade
- ~16 s average hold
- balance DD maximal ~$3.41
- equity DD maximal ~$4.34

## Mandatory QA

1. Explicit target-entry gating for every month partition: start <= entry < end.
2. Warmup data may initialize completed-bar state only.
3. Maximum one chronological opportunity per source per market tick by default.
4. Same-tick multiplicity, if revisited, is explicit pyramiding/scaling, not opportunity count.
5. Every finalist gets full ordered-tick equity-DD replay.
6. Compare every adaptive filter against a simpler constant-cap / lower-exposure control. A filter that only trades less is not automatically an improvement.
7. Parameter neighborhoods must be smooth; single-threshold cliffs are rejected.
8. No August access.

## Engine library — diagnostic species, not calendar modes

Existing causal specialist families may be routed only by contemporaneous market state:
- high-renewal fast continuation/watchdog;
- medium/long exact-state continuation;
- persistent NY17 trend inventory;
- reverse/failed-ignition specialist where independently validated;
- STMR structural session/timeframe parent.

Historical month-native discoveries may teach which state features matter, but month identity itself is forbidden.

## Regime vector v1

### Axis A — directional structure
- completed H4/H1/M15/M5 state tuple;
- HTF coherence score;
- state age;
- M1/M5 Kaufman-style efficiency ratio;
- turn/chop density.

### Axis B — volatility / expansion
- short realized-volatility or ATR proxy;
- ratio to rolling long-horizon baseline;
- session-normalized percentile / robust z-score;
- spread-to-realized-movement ratio.

### Axis C — stability / change
- causal CUSUM-style structural-break pressure;
- regime age / hysteresis;
- recent child-renewal success rate;
- recent realized hold-time elongation;
- failed favorable-extension rate.

## Compatibility states

- TREND_EXPANSION: allow trend inventory / favorable-only pyramiding.
- ORDERLY_CONTINUATION: allow fast renewal/harvest.
- TRANSITION: scouts only; lower cap and shorter lifecycle.
- CHOP_RANDOM: trend specialists restricted; only independently validated reversal/fade species may trade.
- VOL_SHOCK: new exposure restricted; existing profitable inventory governed rather than indiscriminately closed.

## Independent risk governor

State machine:
NORMAL -> CAUTION -> RESTRICTED -> LOCKDOWN

Inputs:
- rolling realized gross-loss acceleration;
- peak-to-current equity drawdown;
- floating adverse excursion / heat;
- rapid deterioration;
- recovery stability.

Actions affect NEW exposure first:
- cap multiplier;
- minimum re-entry delay;
- specialist eligibility;
- cooldown;
- hard lockdown only for severe pressure.

## Validation protocol

Research may inspect Jan/Feb to design feature families, but deployable thresholds must be:
- fixed from prior partitions, OR
- rolling/self-normalized using only past data.

Forward chronology:
- freeze first router family;
- evaluate Mar, Apr, May, Jun, Jul without month-specific retuning;
- report each month separately;
- require positive/acceptable transfer before promotion.

## Promotion objective

A candidate is not promoted merely because net rises.

Rank jointly on:
1. net capture vs matched R9 SYNTH;
2. gross-loss ratio vs matched R9 SYNTH;
3. full tick-level equity DD;
4. PF and expectancy;
5. win rate;
6. unique chronological trade/opportunity density;
7. positive-month count and worst-month behavior;
8. parameter stability.

The preferred frontier improves loss/DD materially while preserving a large fraction of discovered net.

## First bounded hypotheses

H1: 3-axis compatibility matrix (structure + vol + CUSUM) with hysteresis.
H2: renewal-decay watchdog using rolling session-relative success/hold distributions.
H3: unified-stop profitable pyramid inside TREND_EXPANSION only.
H4: loss-pressure governor above H1-H3.
H5: later, only if needed: entropy/HMM/HSMM as second-generation classifiers.

No calendar-month routing. R9 SYNTH remains the hard target.
