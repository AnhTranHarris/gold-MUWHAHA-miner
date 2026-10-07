# GAMMA-02 — Market-Aware Risk Checkpoint 001

**Status:** MAJOR MONTH-BLIND RISK-CONTROL DISCOVERY — ROUTER INTEGRATION PENDING  
**Parent prereg:** GAMMA_02_MARKET_AWARE_UNIVERSAL_ROUTER_PREREG.md  
**August:** SEALED  
**MQL5:** NOT AUTHORIZED

## Owner objective reset

High January net is not sufficient. Promotion now requires:
- high net capture;
- materially lower gross loss;
- materially lower balance and full-tick equity drawdown;
- month-blind causal market awareness;
- no January/February/etc execution mode.

Month identity remains evaluation metadata only.

## Exact R9 SYNTH references

January:
- net +$41,520.82
- 27,980 trades
- PF 23.7154119275
- 87.0908% wins
- +$1.483946 expectancy/trade
- 16.4627s avg hold
- inferred gross loss ~-$1,827.87
- inferred gross profit ~+$43,348.69

Jan-Jul:
- net +$309,122.85
- gross profit +$325,361.51
- gross loss -$16,238.66
- PF 20.036229
- 219,342 trades
- 87.14% wins
- +$1.409319 expectancy/trade
- whole-report balance DD maximal ~$3.41
- whole-report equity DD maximal ~$4.34

January-specific R9 SYNTH DD has not yet been extracted and must not be invented.

## Discovery A — shadow-stall governor

Mechanism:
- maintain a causal virtual/shadow copy of the specialist;
- allow the shadow desk to stay informed even while real exposure is throttled;
- block/reduce NEW real exposure when unresolved virtual inventory ages beyond a threshold.

Representative watchdog119 research point:
- real cap 224;
- oldest unresolved shadow age <=120s required.

January:
- +$41,756.01
- 23,505 trades
- PF 74.043
- gross loss -$571.66
- realized balance DD ~$296.02
- avg hold ~28.33s

This exceeds January R9 SYNTH net while gross loss is roughly one-third of January SYNTH's inferred gross loss. It is NOT yet full-tick equity-DD certified and does not solve later regimes by itself.

## Discovery B — profit-funded capacity

Core rule:
> the market must pay for additional aggression.

Each session/day begins with a small base position allowance. Additional slots unlock only after same-session REALIZED profit finances them. Losses never expand capacity. The rule is causal and contains no calendar-month feature.

### Watchdog119 funded desk

Frozen research geometry:
- base cap 64
- +64 slots per +$2,000 same-day realized profit
- hard cap 256
- daily reset

| Eval month | Net | Trades | PF | Gross loss | Realized balance DD |
|---|---:|---:|---:|---:|---:|
| Jan | **+$48,539.30** | 26,890 | **75.293** | **-$653.35** | ~$296 |
| Feb | +$359.87 | 1,746 | 1.229 | -$1,570.82 | ~$565 |
| Mar | +$2,031.41 | 4,304 | 1.439 | -$4,625.36 | ~$1,882 |
| Apr | -$21.33 | 130 | 0.861 | -$153.94 | ~$53 |
| May | **-$747.09** | 946 | 0.566 | -$1,719.53 | ~$1,160 |
| Jun | +$153.29 | 720 | 1.207 | -$739.61 | ~$511 |
| Jul | +$226.98 | 724 | 1.402 | -$565.16 | ~$328 |

Disposition:
- 5/7 positive evaluation months;
- January remains above R9 SYNTH net with gross loss far below R9 SYNTH January;
- May loss compressed from watchdog119 raw ~-$7.39K to ~-$747.

### Source114 funded desk

Frozen research geometry:
- base cap 8
- +64 slots per +$250 same-day realized profit
- hard cap 256
- daily reset

| Eval month | Net | Trades | PF | Gross loss | Realized balance DD |
|---|---:|---:|---:|---:|---:|
| Jan | +$28,343.64 | 15,965 | 31.715 | -$922.80 | ~$350 |
| Feb | +$4,078.43 | 6,711 | 2.003 | -$4,065.16 | ~$2,138 |
| Mar | -$515.55 | 527 | 0.517 | -$1,067.73 | ~$528 |
| Apr | +$33.82 | 346 | 1.129 | -$261.78 | ~$100 |
| May | +$215.36 | 417 | 2.388 | -$155.21 | ~$54 |
| Jun | +$130.16 | 391 | 1.452 | -$288.26 | ~$174 |
| Jul | +$3.52 | 129 | 1.039 | -$90.57 | ~$57 |

Disposition:
- 6/7 positive evaluation months;
- complements watchdog119 particularly in May;
- March remains the clear weak month for this species.

### Source115 funded desk

Tested as a late-regime species but materially weaker:
- positive Jan/Jun/Jul;
- negative Feb-Mar-Apr-May.
Not promoted as a primary desk.

## Critical interpretation

This is a more useful universal mechanism than hardcoded month routing:

1. A specialist may exist continuously as a shadow/virtual desk.
2. Market-state compatibility determines whether it is eligible.
3. A small real base desk scouts the current state.
4. Realized same-session profit funds additional slots.
5. Stall/loss pressure contracts NEW exposure.
6. Existing profitable inventory is managed rather than indiscriminately strangled.

The market therefore earns aggression twice:
- first through causal regime compatibility;
- second through realized profitability.

## Opportunity-count QA

Historical 119/114 streams can contain many child tickets on the same market tick.

Therefore:
- **unique chronological opportunity count** = at most one opportunity per source per market tick;
- **pyramid multiplicity** = extra same-tick tickets, tracked explicitly as exposure scaling.

No future report may silently call pyramid multiplicity independent opportunity velocity.

## Next unit

`GAMMA_02_MARKET_AWARE_MULTI_DESK_ROUTER_002`

Required:
1. integrate funded119 and funded114 in ONE chronological ledger;
2. one explicit global heat/cap;
3. no arithmetic addition of separately backtested profits;
4. causal pre-session/regime features + live shadow-health;
5. compare against a simple always-on funded multi-desk baseline;
6. rank on net, gross loss, PF, unique opportunity density, realized DD, then full-tick equity DD.

R9 SYNTH remains the hard target.
