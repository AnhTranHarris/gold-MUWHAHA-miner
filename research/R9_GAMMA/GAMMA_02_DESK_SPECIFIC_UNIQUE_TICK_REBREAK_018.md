# GAMMA-02 — Desk-Specific Unique-Tick Rebreak 018

**Status:** COMPLETE JANUARY DISCOVERY — CURRENT CONSERVATIVE OPPORTUNITY BASE  
**Parent:** GAMMA_02_SELECTIVE_REBREAK_LATENCY_017.md  
**Opportunity counting:** maximum one new ticket per source per market tick  
**August:** SEALED

London/overlap and NY17 were allowed independent pullback/reclaim reset geometry.

## Best cap-128 result

- London/overlap reset: **$0.05**
- London/overlap minimum reset latency: **0 ms**
- NY17 reset: **$0.50**
- NY17 minimum reset latency: **1,000 ms**

Economics:
- **+$82,329.33 net**
- **10,907 trades**
- **PF 5.51051**
- **+$7.54830 expectancy/trade**
- realized balance DD ~$2,804.18
- max open 128

Versus conservative one-event-per-tick parent:
- +$5,280.21 additional January net
- +556 completed trades
- PF improves from 5.3715 to 5.5105
- expectancy improves from +$7.4436 to +$7.5483

## Interpretation

A single reset rule is rejected.

London/overlap benefits from shallow $0.05 pullback/reclaim recycling, consistent with dense auction rotation inside an already-approved trend state.

NY17 benefits from a materially deeper $0.50 pullback that must persist at least one second before reclaim, consistent with a slower trend-inventory campaign.

This is causal and adds genuinely time-separated opportunities. Same-tick ladder multiplicity remains excluded from opportunity-count claims.

## Durable artifacts

Library:
`/xauusd-trading-bot/r9-gamma-02-velocity-geometry/2026-10-07/m1-density/`

- gamma02_rebreak_desk_specific_018.py
- gamma02_rebreak_desk_specific_018_london.json
- gamma02_rebreak_desk_specific_018_ny17.json

## Next

Test another independent chronological opportunity factory:
- bounded campaign heartbeat / state-age re-entry under exact high-quality state permission,
- explicit refractory time and favorable-side requirement,
- union/dedup with primary + desk-specific rebreak base,
- no same-tick duplicate scaling.

No MQL5 build. No Jan-Jul promotion yet. R9 SYNTH remains the hard target.
