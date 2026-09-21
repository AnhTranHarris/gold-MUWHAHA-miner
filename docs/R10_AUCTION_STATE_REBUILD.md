# R10 Auction-State Rebuild

## Status

**Compile/test candidate only. Not MT5-certified yet.**

This rebuild supersedes the old R10 server-time session-profile candidate. It carries forward only mechanisms that survived the later causal Jan-July 2026 research and that can be reconstructed exactly enough to implement in MQL5.

August 2026 remains sealed and is not part of development, threshold selection, or certification preparation.

## Authoritative EA

`Experts/GoldMuwahahaMiner_R10_AuctionState.mq5`

The older `GoldMuwahahaMiner_R10_SessionRegime.mq5` is historical/deprecated and is retained on this branch only for traceability. It is not the authoritative R10 implementation.

## What R10 now implements

### 1. R9 causal event population

The minute-bracket/event machinery is retained because the later CONTINUE/FADE research was performed on the R9 REAL event population.

Frozen event geometry:

- total minute bracket width: 30 Hunter pips (`0.30` when `HunterPipPrice=0.01`)
- 10-second completed-S1 velocity/efficiency/range state
- minimum 10-second velocity: 15 Hunter pips
- minimum directional efficiency: 0.70
- minimum 10-second range: 50 Hunter pips
- maximum turns: 9
- maximum same-minute rearms: 3

The R9 M5 ATR/spread eligibility layer is retained to preserve the researched population:

- M5 ATR(14)
- maximum spread: 25 points
- London ATR minimum: 2.00
- overlap ATR minimum: 1.75
- New York ATR minimum: 1.75
- off-session ATR minimum: 2.50

This is an eligibility modifier, **not** the retired R10 server-time execution-profile strategy.

### 2. Transparent CONTINUE / FADE / ABSTAIN router

The latest completed one-second microbar is evaluated relative to the original R9 boundary direction.

#### Balanced-strengthened profile (default)

- `CONTINUE` original boundary direction when:
  - aligned 1-second displacement `<= -0.255`
  - completed 1-second range `>= 0.285`
- `FADE` original boundary direction when:
  - aligned 1-second displacement `>= +0.275`
  - at least 5 ticks occurred in that completed second
- otherwise: `ABSTAIN`

#### Defensive profile

- CONTINUE displacement `<= -0.290`
- FADE displacement `>= +0.310`
- same range/tick-quality requirements

The router uses only completed pre-entry information. No future tick, MFE, MAE, or retrospective ordering is used to select the action.

### 3. Tight harvest lifecycle

Carried-forward lifecycle:

- emergency stop room: `$5.00` of XAUUSD price movement
- harvest ignition: `+$0.01` favorable excursion
- high-water trail: `$0.01`
- maximum hold: 120 seconds
- broker stop-level and tick-size constraints are respected

This deliberately separates catastrophic room from normal profit harvesting. It does **not** tighten the emergency stop merely to improve historical drawdown.

### 4. Ten-second same-direction catastrophe memory

When a position exits by an unharvested losing Stop Loss, the same **traded direction** is blocked for 10 seconds.

- opposite-direction auctions remain eligible
- a blocked event is consumed rather than delayed until the memory expires
- this is not a generic cooldown

### 5. One-position causal state machine

The rebuild remains one-position-at-a-time and preserves the original boundary-event lineage:

- each new minute creates a fresh two-sided boundary
- ambiguous router state means no forced trade
- after a trade closes within the same minute, the opposite **original event boundary** may re-arm
- if a trade survives into another minute, the old boundary is not re-armed

### 6. XAUUSD-only guard

R10 refuses initialization on symbols whose names do not contain `XAUUSD` unless the explicit guard input is disabled.

## What is intentionally NOT encoded yet

### Five-scale P8/P9/P11/P12/P13 portfolio

The research history preserves its measured results and the 1m/3m/5m/10m/20m concept, but the repository does not currently contain the exact event-generator implementation or a reproducible event ledger. Reconstructing those rules from summary statistics would risk lineage drift, so this rebuild does not pretend that layer exists.

### Opposition heat

Opposition heat mattered in the multi-sleeve portfolio. This EA is one-position-at-a-time, so concurrent opposite portfolio exposure cannot occur inside this implementation. It should be added only when the exact multi-sleeve engine is restored.

### HARVEST-to-RUNNER ML promotion

Not promoted. The later causal tests produced too little out-of-sample uplift to justify the added complexity.

### Failed-state hazard modifier

Preserved as a research candidate, but not activated in this code because it has not yet been proven incremental after the strengthened router and catastrophe-memory integration.

### Old R10 five server-time execution profiles

Removed. Later research found that global time/session suppression was not the primary edge and often removed profitable activity.

## Required MT5 test protocol

Before any demo-forward decision:

1. Compile `GoldMuwahahaMiner_R10_AuctionState.mq5` in MetaEditor with **zero errors**.
2. Test XAUUSD using **Every tick based on real ticks**.
3. Development/certification preparation period: **January 1 through July 31, 2026**.
4. Do not open or optimize against August.
5. Run at least these starting balances separately:
   - `$100`
   - `$200`
6. For every month January through July record:
   - net profit
   - gross loss
   - maximum drawdown in dollars
7. Also record overall Jan-July:
   - net profit
   - gross profit
   - gross loss
   - profit factor
   - maximum equity drawdown in dollars
   - total trades
8. For $100 and $200 specifically report:
   - minimum equity reached
   - whether the account breaches the project survival boundary before reaching $500
   - margin failures / rejected trades, if any
9. Compare Balanced and Defensive router profiles without changing any other parameter.

## Research benchmarks

These are research references, not promises for this EA:

- R9 SYNTH Jan-July net reference: approximately `+$309,122.85`
- later five-scale R10 research frontier: approximately `+$309K to +$317K`, depending on catastrophe-memory setting
- current goal: preserve or exceed the R9 SYNTH net reference while materially compressing gross loss and maintaining small-account survivability

The MT5 real-tick test is the authority. If this rebuild fails there, the code is not promoted regardless of Python research results.
